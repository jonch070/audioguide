"""
Descriptor Analysis Backends - Pluggable abstraction layer

This module provides a pluggable system for descriptor analysis, allowing AudioGuide
to use different analysis tools (IRCAM, FluCoMa, Librosa, etc.) interchangeably.

Backends are selected via the DESCRIPTOR_ANALYSIS_TOOL config option.

Available backends:
- 'ircam' (default): IRCAM descriptor analysis (current AudioGuide system)
- 'flucoma': FluCoMa analysis toolkit (requires flucoma-python package)
- More backends can be added in the future (librosa, essentia, aubio, etc.)
"""

import os
import numpy as np
from abc import ABC, abstractmethod


class DescriptorBackend(ABC):
    """
    Base class for descriptor analysis backends.

    All backends must implement these methods to extract fundamental frequency (f0)
    and other descriptors from audio files.
    """

    def __init__(self, verbose=False):
        self.verbose = verbose

    @abstractmethod
    def analyze_file(self, audio_path):
        """
        Analyze an audio file and extract descriptors.

        Args:
            audio_path: Path to audio file

        Returns:
            Dictionary with at least:
            {
                'f0': float,           # Fundamental frequency in Hz (0 if detection failed)
                'success': bool,       # Whether analysis succeeded
                'error': str or None   # Error message if failed
            }

            May include additional descriptors depending on backend.
        """
        pass

    @abstractmethod
    def get_name(self):
        """Return human-readable name of this backend."""
        pass


class IRCAMBackend(DescriptorBackend):
    """
    IRCAM descriptor analysis backend.

    NOTE: This backend is NOT actually needed for normal AudioGuide operation!
    AudioGuide's existing descriptor system already computes IRCAM descriptors
    for all corpus files, and these are accessed via seg.desc.get('f0-seg').

    This backend exists mainly as a reference implementation and fallback.
    In practice, you should simply NOT set DESCRIPTOR_ANALYSIS_TOOL to use
    the existing IRCAM descriptors (which is faster and better integrated).

    This backend is included for:
    1. Reference implementation for other backends
    2. Future use if custom IRCAM re-analysis is needed
    3. Completeness of the backend system
    """

    def __init__(self, verbose=False):
        super().__init__(verbose)
        if verbose:
            print("WARNING: IRCAMBackend is not needed - use default descriptors instead")
            print("(Don't set DESCRIPTOR_ANALYSIS_TOOL for standard IRCAM analysis)")

    def analyze_file(self, audio_path):
        """
        Placeholder - IRCAM descriptors are already computed by AudioGuide.

        Returns failure to indicate that default IRCAM descriptors should be used.
        """
        return {
            'f0': 0.0,
            'success': False,
            'error': 'IRCAMBackend not implemented - use default IRCAM descriptors'
        }

    def get_name(self):
        return "IRCAM (use default descriptors instead)"


class FluCoMaBackend(DescriptorBackend):
    """
    FluCoMa descriptor analysis backend.

    Uses the FluCoMa CLI tools for pitch detection and descriptor extraction.
    Requires: fluid-pitch, fluid-mfcc, fluid-spectralshape, fluid-loudness commands in PATH
    (install from https://www.flucoma.org/download/)

    Falls back to IRCAM if FluCoMa CLI is not installed.
    """

    # Default FFT settings matching AudioGuide's descriptor computation
    DEFAULT_FFT_SIZE = 2048
    DEFAULT_HOP_SIZE = 1024

    def __init__(self, verbose=False):
        super().__init__(verbose)
        self.flucoma_available = False
        self.fallback_backend = None

        # Check availability of all FluCoMa CLI tools
        import shutil
        self.tools = {
            'pitch': shutil.which('fluid-pitch'),
            'mfcc': shutil.which('fluid-mfcc'),
            'spectralshape': shutil.which('fluid-spectralshape'),
            'loudness': shutil.which('fluid-loudness'),
        }

        # Check if at least pitch is available (minimum requirement)
        if self.tools['pitch']:
            self.flucoma_available = True
            self.fluid_pitch_path = self.tools['pitch']
            if self.verbose:
                # Get version
                import subprocess
                try:
                    version_output = subprocess.check_output(
                        [self.fluid_pitch_path, '--help'],
                        stderr=subprocess.STDOUT,
                        text=True
                    )
                    version_line = [l for l in version_output.split('\n') if 'version' in l.lower()]
                    version_str = version_line[0] if version_line else "unknown version"
                    print(f"FluCoMa backend initialized ({version_str})")
                    
                    # Report available tools
                    available = [k for k, v in self.tools.items() if v]
                    print(f"  Available tools: {', '.join(available)}")
                except:
                    print("FluCoMa backend initialized")
        else:
            if self.verbose:
                print("WARNING: FluCoMa CLI tools not found in PATH")
                print("Install from: https://www.flucoma.org/download/")
                print("Falling back to IRCAM backend.")

            # Create fallback to IRCAM
            self.fallback_backend = IRCAMBackend(verbose=verbose)

    def analyze_file(self, audio_path, descriptors=None):
        """
        Analyze using FluCoMa CLI tools for pitch detection and descriptor extraction.

        Args:
            audio_path: Path to audio file
            descriptors: Optional list of descriptor types to extract.
                        Supported: 'mfcc', 'spectralshape', 'loudness', 'pitch'
                        If None, extracts only pitch (backward compatible).

        Returns:
            Dictionary with at least:
            {
                'f0': float,           # Fundamental frequency in Hz (0 if detection failed)
                'success': bool,       # Whether analysis succeeded
                'error': str or None   # Error message if failed
            }

            May include additional descriptors depending on backend and requested descriptors.
        """
        # Default to pitch only for backward compatibility
        if descriptors is None:
            descriptors = ['pitch']
        
        # Fallback if FluCoMa not available
        if not self.flucoma_available:
            return self.fallback_backend.analyze_file(audio_path)

        result = {
            'f0': 0.0,
            'success': True,
            'error': None,
        }

        try:
            # Extract requested descriptors
            for desc_type in descriptors:
                if desc_type == 'pitch':
                    pitch_result = self._extract_pitch(audio_path)
                    result['f0'] = pitch_result.get('f0', 0.0)
                    result['pitch_data'] = pitch_result.get('pitch_data')
                elif desc_type == 'mfcc':
                    result['mfcc'] = self._extract_mfcc(audio_path)
                elif desc_type == 'spectralshape':
                    result['spectralshape'] = self._extract_spectralshape(audio_path)
                elif desc_type == 'loudness':
                    result['loudness'] = self._extract_loudness(audio_path)
                else:
                    if self.verbose:
                        print(f"WARNING: Unknown descriptor type '{desc_type}'")

            return result

        except Exception as e:
            if self.verbose:
                print(f"WARNING: FluCoMa analysis failed for {audio_path}: {e}")

            # Try fallback to IRCAM
            if self.fallback_backend:
                if self.verbose:
                    print(f"  Falling back to IRCAM for {audio_path}")
                return self.fallback_backend.analyze_file(audio_path)

            return {
                'f0': 0.0,
                'success': False,
                'error': str(e)
            }

    def _extract_pitch(self, audio_path):
        """
        Extract pitch using fluid-pitch.

        Args:
            audio_path: Path to audio file

        Returns:
            Dictionary with 'f0' and 'pitch_data'
        """
        import subprocess
        import tempfile
        import soundfile as sf
        import os

        # Create temporary output file for pitch data
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp_output:
            output_path = tmp_output.name

        try:
            # Run fluid-pitch CLI
            # Algorithm: 0=cepstrum, 1=harmonic product spectrum, 2=YIN (default)
            cmd = [
                self.tools['pitch'],
                '-source', audio_path,
                '-features', output_path,
                '-algorithm', '2',  # YIN algorithm
                '-minfreq', '80',
                '-maxfreq', '2000',
                '-fftsettings', str(self.DEFAULT_FFT_SIZE), str(self.DEFAULT_HOP_SIZE)
            ]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True
            )

            # Read the pitch data from output file
            pitch_data, sr = sf.read(output_path)

            # Extract pitch values (first column is pitch in Hz, second is confidence)
            if len(pitch_data.shape) == 1:
                pitches = pitch_data
            else:
                pitches = pitch_data[:, 0]  # First column is pitch

            # Extract median pitch from voiced frames (pitch > 0)
            voiced_pitches = pitches[pitches > 0]

            if len(voiced_pitches) == 0:
                return {
                    'f0': 0.0,
                    'pitch_data': pitches,
                    'success': False,
                    'error': 'No pitched content detected'
                }

            # Use median pitch as representative f0
            f0 = float(np.median(voiced_pitches))

            return {
                'f0': f0,
                'pitch_data': pitches,
                'success': True,
                'error': None
            }

        finally:
            # Clean up temp file
            if os.path.exists(output_path):
                os.unlink(output_path)

    def _extract_mfcc(self, audio_path):
        """
        Extract MFCC coefficients using fluid-mfcc.

        Args:
            audio_path: Path to audio file

        Returns:
            Dictionary with MFCC coefficients and metadata
        """
        import subprocess
        import tempfile
        import soundfile as sf
        import os

        # Get MFCC count from config or use default
        try:
            from audioguide import defaults
            num_coeffs = getattr(defaults, 'FLUCOMA_MFCC_COUNT', 13)
        except ImportError:
            num_coeffs = 13

        # Create temporary output file for MFCC data
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp_output:
            output_path = tmp_output.name

        try:
            # Run fluid-mfcc CLI
            cmd = [
                self.tools['mfcc'],
                '-source', audio_path,
                '-mfcc', output_path,
                '-numcoeffs', str(num_coeffs),
                '-fftsettings', str(self.DEFAULT_FFT_SIZE), str(self.DEFAULT_HOP_SIZE)
            ]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True
            )

            # Read the MFCC data from output file
            mfcc_data, sr = sf.read(output_path)

            # MFCC output: frames x (numCoeffs + 1) - first column is RMS
            # Extract just the MFCC coefficients (skip RMS)
            if len(mfcc_data.shape) == 2:
                mfcc_coeffs = mfcc_data[:, 1:]  # Skip RMS column
            else:
                mfcc_coeffs = mfcc_data.reshape(-1, 1)

            # Compute statistics across frames for each coefficient
            mfcc_stats = {
                'mean': np.mean(mfcc_coeffs, axis=0).tolist(),
                'std': np.std(mfcc_coeffs, axis=0).tolist(),
                'min': np.min(mfcc_coeffs, axis=0).tolist(),
                'max': np.max(mfcc_coeffs, axis=0).tolist(),
            }

            return {
                'coefficients': mfcc_coeffs,
                'statistics': mfcc_stats,
                'num_coefficients': num_coeffs,
                'sample_rate': sr,
                'success': True,
                'error': None
            }

        finally:
            # Clean up temp file
            if os.path.exists(output_path):
                os.unlink(output_path)

    def _extract_spectralshape(self, audio_path):
        """
        Extract spectral shape descriptors using fluid-spectralshape.

        Spectral shape descriptors include:
        - Centroid, Spread, Skewness, Kurtosis
        - Flatness, Rolloff, Slope

        Args:
            audio_path: Path to audio file

        Returns:
            Dictionary with spectral shape descriptors
        """
        import subprocess
        import tempfile
        import soundfile as sf
        import os

        # Create temporary output file for spectral shape data
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp_output:
            output_path = tmp_output.name

        try:
            # Run fluid-spectralshape CLI
            cmd = [
                self.tools['spectralshape'],
                '-source', audio_path,
                '-features', output_path,
                '-fftsettings', str(self.DEFAULT_FFT_SIZE), str(self.DEFAULT_HOP_SIZE)
            ]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True
            )

            # Read the spectral shape data from output file
            # Output format: frames x 7 (centroid, spread, skewness, kurtosis, flatness, rolloff, slope)
            spectral_data, sr = sf.read(output_path)

            # Compute statistics across frames for each descriptor
            descriptor_names = ['centroid', 'spread', 'skewness', 'kurtosis', 'flatness', 'rolloff', 'slope']
            spectral_stats = {}

            for i, name in enumerate(descriptor_names):
                if spectral_data.shape[1] > i:
                    col_data = spectral_data[:, i]
                    spectral_stats[name] = {
                        'mean': float(np.mean(col_data)),
                        'std': float(np.std(col_data)),
                        'min': float(np.min(col_data)),
                        'max': float(np.max(col_data)),
                    }

            return {
                'descriptors': spectral_stats,
                'raw_data': spectral_data,
                'sample_rate': sr,
                'success': True,
                'error': None
            }

        finally:
            # Clean up temp file
            if os.path.exists(output_path):
                os.unlink(output_path)

    def _extract_loudness(self, audio_path):
        """
        Extract loudness (LUFS) using fluid-loudness.

        Args:
            audio_path: Path to audio file

        Returns:
            Dictionary with loudness descriptors
        """
        import subprocess
        import tempfile
        import soundfile as sf
        import os

        # Create temporary output file for loudness data
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp_output:
            output_path = tmp_output.name

        try:
            # Run fluid-loudness CLI
            cmd = [
                self.tools['loudness'],
                '-source', audio_path,
                '-features', output_path
            ]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True
            )

            # Read the loudness data from output file
            # Output format: frames x 2 (loudness, true_peak)
            loudness_data, sr = sf.read(output_path)

            # Extract loudness values
            loudness_vals = loudness_data[:, 0] if len(loudness_data.shape) == 2 else loudness_data

            # Compute statistics
            loudness_stats = {
                'mean': float(np.mean(loudness_vals)),
                'std': float(np.std(loudness_vals)),
                'min': float(np.min(loudness_vals)),
                'max': float(np.max(loudness_vals)),
            }

            # True peak (second column)
            if len(loudness_data.shape) == 2 and loudness_data.shape[1] > 1:
                loudness_stats['true_peak'] = float(np.max(loudness_data[:, 1]))

            return {
                'loudness': loudness_stats,
                'raw_data': loudness_vals,
                'sample_rate': sr,
                'success': True,
                'error': None
            }

        finally:
            # Clean up temp file
            if os.path.exists(output_path):
                os.unlink(output_path)

    def get_name(self):
        if self.flucoma_available:
            return "FluCoMa"
        else:
            return "FluCoMa (unavailable, using IRCAM fallback)"


class LibrosaBackend(DescriptorBackend):
    """
    Librosa descriptor analysis backend.

    Uses Librosa's pYIN algorithm for pitch detection and descriptor extraction.
    Requires: pip install librosa

    Falls back to IRCAM if Librosa is not installed.
    """

    def __init__(self, verbose=False):
        super().__init__(verbose)
        self.librosa_available = False
        self.fallback_backend = None

        # Try to import Librosa
        try:
            import librosa
            self.librosa = librosa
            self.librosa_available = True

            if self.verbose:
                print(f"Librosa backend initialized (version {librosa.__version__})")

        except ImportError:
            if self.verbose:
                print("WARNING: Librosa not installed. Install with: pip install librosa")
                print("Falling back to IRCAM backend.")

            # Create fallback to IRCAM
            self.fallback_backend = IRCAMBackend(verbose=verbose)

    def analyze_file(self, audio_path):
        """
        Analyze using Librosa pYIN pitch detection.

        Uses Librosa's pYIN algorithm for fundamental frequency estimation.
        Falls back to IRCAM if Librosa is not available.
        """
        # Fallback if Librosa not available
        if not self.librosa_available:
            return self.fallback_backend.analyze_file(audio_path)

        try:
            # Load audio
            y, sr = self.librosa.load(audio_path, sr=None, mono=True)

            # Use pYIN for pitch detection
            f0, voiced_flag, voiced_probs = self.librosa.pyin(
                y,
                sr=sr,
                fmin=self.librosa.note_to_hz('C2'),  # ~65 Hz
                fmax=self.librosa.note_to_hz('C7'),  # ~2093 Hz
                frame_length=2048
            )

            # Extract median pitch from voiced frames
            voiced_f0 = f0[voiced_flag]

            if len(voiced_f0) == 0:
                if self.verbose:
                    print(f"WARNING: Librosa pYIN found no pitched content in {audio_path}")
                return {
                    'f0': 0.0,
                    'success': False,
                    'error': 'No pitched content detected'
                }

            # Use median pitch as representative f0
            median_f0 = float(np.nanmedian(voiced_f0))

            return {
                'f0': median_f0,
                'success': True,
                'error': None,
                'pitch_data': f0,  # Optional: full pitch track
                'voiced_flag': voiced_flag,
                'voiced_probs': voiced_probs
            }

        except Exception as e:
            if self.verbose:
                print(f"WARNING: Librosa analysis failed for {audio_path}: {e}")

            # Try fallback to IRCAM
            if self.fallback_backend:
                if self.verbose:
                    print(f"  Falling back to IRCAM for {audio_path}")
                return self.fallback_backend.analyze_file(audio_path)

            return {
                'f0': 0.0,
                'success': False,
                'error': str(e)
            }

    def get_name(self):
        if self.librosa_available:
            return "Librosa"
        else:
            return "Librosa (unavailable, using IRCAM fallback)"


# Backend registry
AVAILABLE_BACKENDS = {
    'ircam': IRCAMBackend,
    'flucoma': FluCoMaBackend,
    'librosa': LibrosaBackend,
}


def get_backend(backend_name='ircam', verbose=False):
    """
    Factory function to get a descriptor analysis backend.

    Args:
        backend_name: Name of backend ('ircam', 'flucoma', etc.)
        verbose: Whether to print verbose output

    Returns:
        DescriptorBackend instance

    Raises:
        ValueError: If backend_name is not recognized
    """
    backend_name = backend_name.lower()

    if backend_name not in AVAILABLE_BACKENDS:
        available = ', '.join(AVAILABLE_BACKENDS.keys())
        raise ValueError(
            f"Unknown descriptor backend '{backend_name}'. "
            f"Available backends: {available}"
        )

    backend_class = AVAILABLE_BACKENDS[backend_name]
    return backend_class(verbose=verbose)


def list_backends():
    """
    List all available descriptor backends.

    Returns:
        List of backend names
    """
    return list(AVAILABLE_BACKENDS.keys())
