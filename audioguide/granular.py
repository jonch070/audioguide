"""
AudioGuide Granular Synthesis Module

Provides granular synthesis functionality for spectral reconstruction.
Breaks corpus sounds into small grains for more natural-sounding output.
"""

import numpy as np
from typing import List, Tuple, Optional, Generator


class GrainGenerator:
    """
    Generates grains from audio for granular synthesis.
    
    Supports configurable grain size, overlap, and variance parameters
    for creating natural-sounding reconstructions.
    """
    
    def __init__(self, audio: np.ndarray, sr: int, 
                 grain_size_ms: float = 50.0,
                 hop_size_ms: Optional[float] = None,
                 overlap: float = 0.5,
                 envelope: str = 'hanning'):
        """
        Initialize grain generator.
        
        Args:
            audio: Input audio signal
            sr: Sample rate
            grain_size_ms: Grain size in milliseconds
            hop_size_ms: Hop between grains (None = auto-calculate)
            overlap: Overlap ratio (0-1)
            envelope: Grain envelope type ('hanning', 'cosine', 'rectangular')
        """
        self.audio = audio
        self.sr = sr
        self.grain_size_samples = int(grain_size_ms * sr / 1000)
        self.grain_size_ms = grain_size_ms
        
        # Calculate hop size
        if hop_size_ms is not None:
            self.hop_size_samples = int(hop_size_ms * sr / 1000)
        else:
            self.hop_size_samples = int(self.grain_size_samples * (1 - overlap))
        
        self.overlap = overlap
        self.envelope_type = envelope
        
        # Pre-compute envelope
        self.envelope = self._create_envelope()
    
    def _create_envelope(self) -> np.ndarray:
        """Create grain envelope."""
        n = self.grain_size_samples
        if self.envelope_type == 'hanning':
            return np.hanning(n)
        elif self.envelope_type == 'cosine':
            return np.sin(np.pi * np.arange(n) / (n - 1))
        elif self.envelope_type == 'rectangular':
            return np.ones(n)
        else:
            return np.hanning(n)  # Default to hanning
    
    def generate_grains(self, start_sample: int, num_grains: int = 1,
                        pitch_variance: float = 0.0,
                        amp_variance: float = 0.0,
                        pos_variance: float = 0.0) -> List[Tuple[np.ndarray, float]]:
        """
        Generate grains from audio starting at given position.
        
        Args:
            start_sample: Starting position in audio (samples)
            num_grains: Number of grains to generate
            pitch_variance: Pitch variance in semitones
            amp_variance: Amplitude variance (0-1)
            pos_variance: Position variance ratio (0-1)
            
        Returns:
            List of (grain_array, amplitude) tuples
        """
        grains = []
        
        for i in range(num_grains):
            # Calculate position with optional variance
            if pos_variance > 0 and i > 0:
                # Random offset within hop size
                offset = int(pos_variance * self.hop_size_samples * (np.random.random() - 0.5))
            else:
                offset = 0
            
            pos = start_sample + i * self.hop_size_samples + offset
            
            # Extract grain (with wrapping or zero-padding)
            grain = self._extract_grain(pos)
            
            # Apply pitch variance (via resampling)
            if pitch_variance != 0:
                grain = self._apply_pitch_shift(grain, pitch_variance)
            
            # Apply amplitude variance
            if amp_variance > 0:
                amp_factor = 1.0 + amp_variance * (np.random.random() * 2 - 1)
                amp_factor = max(0.1, min(1.5, amp_factor))  # Clamp
                grain = grain * amp_factor
                amp = np.max(np.abs(grain))
            else:
                amp = np.max(np.abs(grain))
            
            grains.append((grain, amp))
        
        return grains
    
    def _extract_grain(self, position: int) -> np.ndarray:
        """Extract grain at position with envelope applied."""
        n = self.grain_size_samples
        half_n = n // 2
        
        # Handle edge cases with wrapping or zero-padding
        if position < half_n:
            # Near start - pad with zeros
            grain = np.zeros(n)
            start = 0
            end = min(n, position + half_n)
            actual_len = end - start
            grain[n - actual_len:] = self.audio[start:end] * self.envelope[n - actual_len:n]
        elif position + half_n > len(self.audio):
            # Near end - pad with zeros
            grain = np.zeros(n)
            start = max(0, position - half_n)
            actual_len = len(self.audio) - start
            grain[:actual_len] = self.audio[start:] * self.envelope[:actual_len]
        else:
            # Normal case
            grain = self.audio[position - half_n:position + half_n].copy()
            # Ensure envelope matches grain size
            if len(grain) == len(self.envelope):
                grain = grain * self.envelope
            else:
                # Resize envelope to match
                indices = np.linspace(0, len(self.envelope) - 1, len(grain))
                envelope = np.interp(indices, np.arange(len(self.envelope)), self.envelope)
                grain = grain * envelope
        
        return grain
    
    def _apply_pitch_shift(self, grain: np.ndarray, semitones: float) -> np.ndarray:
        """Apply pitch shift via resampling."""
        if semitones == 0:
            return grain
        
        # Calculate ratio
        ratio = 2 ** (semitones / 12)
        
        # Resample
        new_length = int(len(grain) / ratio)
        indices = np.linspace(0, len(grain) - 1, new_length)
        shifted = np.interp(indices, np.arange(len(grain)), grain)
        
        # Resample back to original length
        if len(shifted) < len(grain):
            result = np.zeros(len(grain))
            result[:len(shifted)] = shifted
        else:
            result = shifted[:len(grain)]
        
        return result
    
    def grains_for_duration(self, start_sample: int, duration_sec: float) -> Generator[Tuple[np.ndarray, float], None, None]:
        """
        Generate grains to cover a duration.
        
        Args:
            start_sample: Starting position
            duration_sec: Duration to cover in seconds
            
        Yields:
            (grain, amplitude) tuples
        """
        duration_samples = int(duration_sec * self.sr)
        num_grains = max(1, duration_samples // self.hop_size_samples + 1)
        
        for i in range(num_grains):
            yield from self.generate_grains(start_sample, num_grains=1)


def granular_synthesize(corpus_audio: np.ndarray, corpus_sr: int,
                        target_params: List[Tuple[float, float, float]],
                        grain_size_ms: float = 50.0,
                        overlap: float = 0.5,
                        pitch_variance: float = 0.0,
                        amp_variance: float = 0.1,
                        pos_variance: float = 0.0) -> Tuple[np.ndarray, int]:
    """
    Perform granular synthesis for spectral reconstruction.
    
    Args:
        corpus_audio: Corpus audio to use
        corpus_sr: Sample rate
        target_params: List of (corpus_position, amplitude, pitch_semitones) tuples
        grain_size_ms: Grain size in milliseconds
        overlap: Overlap ratio
        pitch_variance: Pitch variance in semitones
        amp_variance: Amplitude variance
        pos_variance: Position variance
        
    Returns:
        (synthesized_audio, sample_rate)
    """
    if not target_params:
        return np.array([]), corpus_sr
    
    generator = GrainGenerator(
        corpus_audio, corpus_sr,
        grain_size_ms=grain_size_ms,
        overlap=overlap,
        envelope='hanning'
    )
    
    # Calculate output length
    max_pos = max(int(p[0]) for p in target_params)
    duration_sec = max_pos / corpus_sr + grain_size_ms / 1000 * 2
    output_length = int(duration_sec * corpus_sr)
    
    # Accumulator for overlap-add
    output = np.zeros(output_length)
    weights = np.zeros(output_length)
    
    for pos, amp, pitch in target_params:
        pos_sample = int(pos * corpus_sr)
        grains = generator.generate_grains(
            pos_sample, 
            num_grains=1,
            pitch_variance=pitch_variance + pitch,
            amp_variance=amp_variance,
            pos_variance=pos_variance
        )
        
        for grain, grain_amp in grains:
            if len(grain) == 0:
                continue
                
            # Calculate output position
            grain_center = int(pos_sample)
            start = max(0, grain_center - len(grain) // 2)
            end = min(len(output), start + len(grain))
            
            # Insert grain
            grain_start = max(0, -start)
            grain_end = grain_start + (end - start)
            
            if start < 0:
                output[:end] += grain[grain_start:grain_end] * amp
                weights[:end] += np.abs(grain[grain_start:grain_end])
            else:
                output[start:end] += grain[grain_start:grain_end] * amp
                weights[start:end] += np.abs(grain[grain_start:grain_end])
    
    # Normalize by weights
    weights = np.where(weights > 0, weights, 1)
    output = output / weights
    
    return output, corpus_sr


class GranularSpectralMatch:
    """
    Represents a grain-based spectral match for one partial.
    
    Contains multiple grains that together reconstruct a target partial.
    """
    
    def __init__(self, partial_freq: float, partial_amp: float,
                 corpus_segment, grains: List[np.ndarray]):
        self.partial_freq = partial_freq
        self.partial_amp = partial_amp
        self.corpus_segment = corpus_segment
        self.grains = grains
    
    @property
    def duration(self) -> float:
        """Get total duration of grains."""
        if not self.grains:
            return 0.0
        return len(self.grains) * 0.05  # Approximate


def compute_grain_parameters(audio: np.ndarray, sr: int,
                             target_freq: float = 440.0) -> dict:
    """
    Compute optimal grain parameters based on audio content.
    
    Args:
        audio: Audio signal
        sr: Sample rate
        target_freq: Target fundamental frequency
        
    Returns:
        Dictionary with grain_size_ms, overlap, etc.
    """
    # Base grain size on period of target frequency
    period_samples = sr / target_freq if target_freq > 0 else sr / 440
    grain_size_ms = max(10, min(100, period_samples / sr * 1000 * 4))
    
    # Adjust overlap for smoothness
    overlap = 0.5
    
    return {
        'grain_size_ms': grain_size_ms,
        'overlap': overlap,
        'hop_size_ms': grain_size_ms * (1 - overlap)
    }
