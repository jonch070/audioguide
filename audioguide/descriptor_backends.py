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

    Uses the FluCoMa toolkit for pitch detection and descriptor extraction.
    Requires: pip install flucoma-python

    Falls back to IRCAM if FluCoMa is not installed.
    """

    def __init__(self, verbose=False):
        super().__init__(verbose)
        self.flucoma_available = False
        self.fallback_backend = None

        # Try to import FluCoMa
        try:
            import flucoma
            from flucoma.utils import get_buffer
            self.flucoma = flucoma
            self.get_buffer = get_buffer
            self.flucoma_available = True

            if self.verbose:
                print(f"FluCoMa backend initialized (version {flucoma.__version__})")

        except ImportError:
            if self.verbose:
                print("WARNING: FluCoMa not installed. Install with: pip install flucoma-python")
                print("Falling back to IRCAM backend.")

            # Create fallback to IRCAM
            self.fallback_backend = IRCAMBackend(verbose=verbose)

    def analyze_file(self, audio_path):
        """
        Analyze using FluCoMa pitch detection.

        Uses FluCoMa's Pitch algorithm for fundamental frequency estimation.
        Falls back to IRCAM if FluCoMa is not available.
        """
        # Fallback if FluCoMa not available
        if not self.flucoma_available:
            return self.fallback_backend.analyze_file(audio_path)

        try:
            import soundfile as sf

            # Load audio
            audio_data, sr = sf.read(audio_path)

            # Convert to mono if stereo
            if len(audio_data.shape) > 1:
                audio_data = audio_data.mean(axis=1)

            # Use FluCoMa Pitch algorithm
            from flucoma import pitch

            # Analyze pitch across whole file
            pitch_data = pitch(audio_data, sr,
                             algorithm='cepstrum',  # Can also use 'harmonic' or 'yin'
                             minFreq=80,
                             maxFreq=2000,
                             hopSize=512)

            # Extract median pitch (ignore zeros/unvoiced frames)
            pitched_frames = pitch_data[pitch_data > 0]

            if len(pitched_frames) == 0:
                if self.verbose:
                    print(f"WARNING: FluCoMa pitch detection found no pitched content in {audio_path}")
                return {
                    'f0': 0.0,
                    'success': False,
                    'error': 'No pitched content detected'
                }

            # Use median pitch as representative f0
            f0 = float(np.median(pitched_frames))

            return {
                'f0': f0,
                'success': True,
                'error': None,
                'pitch_data': pitch_data  # Optional: full pitch track
            }

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

    def get_name(self):
        if self.flucoma_available:
            return "FluCoMa"
        else:
            return "FluCoMa (unavailable, using IRCAM fallback)"


# Backend registry
AVAILABLE_BACKENDS = {
    'ircam': IRCAMBackend,
    'flucoma': FluCoMaBackend,
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
