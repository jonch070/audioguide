"""
AudioGuide Batch Processing Module

Provides batch processing for processing multiple target files against a corpus.
"""

import os
import json
import time
import glob
from pathlib import Path
from typing import List, Optional, Dict, Any, Callable
from dataclasses import dataclass, asdict, field
from concurrent.futures import ThreadPoolExecutor, as_completed

from audioguide import defaults
from audioguide.cache import get_cache


@dataclass
class BatchResult:
    """Result of processing a single file in batch mode."""
    file_path: str
    success: bool
    output_files: List[str] = field(default_factory=list)
    error: str = ''
    duration_sec: float = 0.0
    
    def to_dict(self):
        return asdict(self)


@dataclass
class BatchSummary:
    """Summary of batch processing run."""
    total_files: int
    successful: int
    failed: int
    total_duration_sec: float
    results: List[BatchResult]
    corpus_path: str = ''
    config_used: Dict = field(default_factory=dict)
    
    def to_dict(self):
        return {
            'total_files': self.total_files,
            'successful': self.successful,
            'failed': self.failed,
            'total_duration_sec': self.total_duration_sec,
            'results': [r.to_dict() for r in self.results],
            'corpus_path': self.corpus_path,
            'config_used': self.config_used
        }


class BatchProcessor:
    """
    Batch processor for processing multiple files.
    """
    
    def __init__(self, input_dir: str, output_dir: str, 
                 pattern: str = '*.wav',
                 continue_on_error: bool = True,
                 workers: Optional[int] = None):
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self.pattern = pattern
        self.continue_on_error = continue_on_error
        self.workers = workers or os.cpu_count() or 4
        
        # Create output directory
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def scan_input_files(self) -> List[Path]:
        """Find all input files matching pattern."""
        pattern_path = self.input_dir / self.pattern
        files = sorted(glob.glob(str(pattern_path)))
        return [Path(f) for f in files]
    
    def process_single(self, file_path: Path, config: Dict) -> BatchResult:
        """Process a single file."""
        start_time = time.time()
        
        try:
            # Import here to avoid circular imports
            from audioguide import concatenate
            
            # Create output subdirectory for this file
            file_output_dir = self.output_dir / file_path.stem
            file_output_dir.mkdir(exist_ok=True)
            
            # Set up config for this file
            file_config = config.copy()
            file_config['TARGET'] = file_path
            file_config['DICT_OUTPUT_FILEPATH'] = str(file_output_dir / 'output.json')
            
            # Run synthesis
            output_files = concatenate(file_config)
            
            duration = time.time() - start_time
            
            return BatchResult(
                file_path=str(file_path),
                success=True,
                output_files=[str(file_output_dir)],
                duration_sec=duration
            )
            
        except Exception as e:
            duration = time.time() - start_time
            
            return BatchResult(
                file_path=str(file_path),
                success=False,
                error=str(e),
                duration_sec=duration
            )
    
    def process_all(self, config: Dict, 
                   progress_callback: Optional[Callable[[int, int], None]] = None) -> BatchSummary:
        """Process all input files."""
        files = self.scan_input_files()
        
        if not files:
            return BatchSummary(
                total_files=0,
                successful=0,
                failed=0,
                total_duration_sec=0,
                results=[],
                corpus_path=config.get('CORPUS', [''])[0] if config.get('CORPUS') else ''
            )
        
        results = []
        successful = 0
        failed = 0
        total_start = time.time()
        
        # Process in parallel with thread pool
        with ThreadPoolExecutor(max_workers=self.workers) as executor:
            futures = {executor.submit(self.process_single, f, config): f for f in files}
            
            completed = 0
            for future in as_completed(futures):
                result = future.result()
                results.append(result)
                
                if result.success:
                    successful += 1
                else:
                    failed += 1
                    if not self.continue_on_error:
                        # Cancel remaining futures
                        for f in futures:
                            f.cancel()
                        break
                
                completed += 1
                if progress_callback:
                    progress_callback(completed, len(files))
        
        total_duration = time.time() - total_start
        
        return BatchSummary(
            total_files=len(files),
            successful=successful,
            failed=failed,
            total_duration_sec=total_duration,
            results=results,
            corpus_path=config.get('CORPUS', [''])[0] if config.get('CORPUS') else '',
            config_used=config
        )


def process_batch(input_dir: str, output_dir: str, 
                 config: Dict,
                 pattern: str = '*.wav',
                 continue_on_error: bool = True,
                 workers: Optional[int] = None,
                 progress_callback: Optional[Callable[[int, int], None]] = None,
                 summary_file: Optional[str] = None) -> BatchSummary:
    """
    Process multiple files in batch mode.
    
    Args:
        input_dir: Directory containing target audio files
        output_dir: Output directory for results
        config: AudioGuide configuration dict
        pattern: Glob pattern for input files
        continue_on_error: Continue if one file fails
        workers: Number of parallel workers
        progress_callback: Called with (completed, total)
        summary_file: Path to save JSON summary
        
    Returns:
        BatchSummary with results
    """
    processor = BatchProcessor(
        input_dir=input_dir,
        output_dir=output_dir,
        pattern=pattern,
        continue_on_error=continue_on_error,
        workers=workers
    )
    
    summary = processor.process_all(config, progress_callback)
    
    # Save summary
    if summary_file:
        with open(summary_file, 'w') as f:
            json.dump(summary.to_dict(), f, indent=2)
    
    return summary


def analyze_corpus_coverage(corpus_path: str) -> Dict:
    """
    Analyze corpus frequency coverage.
    
    Args:
        corpus_path: Path to corpus directory
        
    Returns:
        Dict with coverage analysis
    """
    import numpy as np
    import soundfile as sf
    
    corpus_dir = Path(corpus_path)
    if not corpus_dir.exists():
        return {'error': 'Corpus directory not found'}
    
    # Find all audio files
    audio_files = list(corpus_dir.glob('*.wav')) + list(corpus_dir.glob('*.aif*'))
    
    if not audio_files:
        return {'error': 'No audio files found in corpus'}
    
    # Analyze frequency range
    min_freq = float('inf')
    max_freq = 0
    frequencies = []
    
    for audio_file in audio_files[:50]:  # Sample first 50 for speed
        try:
            data, sr = sf.read(audio_file, duration=1.0)  # First second
            
            if len(data.shape) > 1:
                data = data.mean(axis=1)
            
            # Estimate frequency content using zero crossings
            zero_crossings = np.where(np.diff(np.signbit(data)))[0]
            if len(zero_crossings) > 0:
                est_freq = len(zero_crossings) / (len(data) / sr) / 2
                frequencies.append(est_freq)
                
                if est_freq > 0:
                    min_freq = min(min_freq, est_freq)
                    max_freq = max(max_freq, est_freq)
                    
        except Exception:
            continue
    
    if not frequencies:
        return {'error': 'Could not analyze frequency content'}
    
    return {
        'files_analyzed': len(frequencies),
        'min_frequency': min_freq if min_freq != float('inf') else 0,
        'max_frequency': max_freq,
        'mean_frequency': float(np.mean(frequencies)),
        'coverage': 'Good' if max_freq > 2000 else 'Limited'
    }


def suggest_corpus_improvements(corpus_path: str, target_path: str) -> List[str]:
    """
    Suggest corpus improvements based on target analysis.
    
    Args:
        corpus_path: Path to corpus directory
        target_path: Path to target audio file
        
    Returns:
        List of suggestion strings
    """
    import soundfile as sf
    
    suggestions = []
    
    # Analyze corpus coverage
    corpus_analysis = analyze_corpus_coverage(corpus_path)
    
    if 'error' in corpus_analysis:
        return [corpus_analysis['error']]
    
    # Analyze target
    try:
        data, sr = sf.read(target_path)
        
        if len(data.shape) > 1:
            data = data.mean(axis=1)
        
        import numpy as np
        zero_crossings = np.where(np.diff(np.sign(data)))[0]
        if len(zero_crossings) > 0:
            target_freq = len(zero_crossings) / (len(data) / sr) / 2
            
            if target_freq < corpus_analysis['min_frequency']:
                suggestions.append(f"Target frequency ({target_freq:.0f} Hz) is below corpus range")
            elif target_freq > corpus_analysis['max_frequency']:
                suggestions.append(f"Target frequency ({target_freq:.0f} Hz) is above corpus range")
            else:
                suggestions.append("Target frequency within corpus range")
        
        # Check file count
        if corpus_analysis['files_analyzed'] < 20:
            suggestions.append("Consider adding more files to corpus for better coverage")
            
    except Exception as e:
        suggestions.append(f"Could not analyze target: {e}")
    
    return suggestions
