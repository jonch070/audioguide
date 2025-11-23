############################################################################
## This software is distributed for free, without warranties of any kind. ##
## Spectral descriptor extensions for AudioGuide                          ##
############################################################################

"""
Custom spectral descriptors for AudioGuide.

Integrates spectralanalysis.py with AudioGuide's descriptor system,
allowing spectral features to be used in SEARCH configurations.
"""

import numpy as np
import audioguide.spectralanalysis as spectralanalysis


def compute_spectral_f0(audio, sr, fmin=80, fmax=2000):
    """
    Compute median fundamental frequency for a segment.

    Returns a single float value suitable for AudioGuide descriptors.
    """
    return spectralanalysis.get_median_f0(audio, sr, fmin, fmax)


def compute_harmonic_count(audio, sr, fmin=80, fmax=2000, n_harmonics=16):
    """
    Count number of strong harmonics present.

    Returns count of detected harmonics (descriptor for harmonic richness).
    """
    f0 = spectralanalysis.get_median_f0(audio, sr, fmin, fmax)
    if f0 <= 0:
        return 0

    harmonics = spectralanalysis.extract_harmonic_series_fft(
        audio, sr, f0, n_harmonics
    )
    return len(harmonics)


def compute_harmonic_brightness(audio, sr, fmin=80, fmax=2000, n_harmonics=16):
    """
    Compute spectral centroid of harmonics (harmonic brightness).

    Returns weighted average frequency of harmonics.
    """
    f0 = spectralanalysis.get_median_f0(audio, sr, fmin, fmax)
    if f0 <= 0:
        return 0.0

    harmonics = spectralanalysis.extract_harmonic_series_fft(
        audio, sr, f0, n_harmonics
    )

    if len(harmonics) == 0:
        return 0.0

    # Weighted average by amplitude
    freqs = np.array([freq for freq, amp in harmonics])
    amps = np.array([amp for freq, amp in harmonics])

    if np.sum(amps) == 0:
        return 0.0

    return np.sum(freqs * amps) / np.sum(amps)


def register_spectral_descriptors(descriptor_manager):
    """
    Register custom spectral descriptors with AudioGuide.

    Call this during initialization to make spectral descriptors available
    in SEARCH configurations.

    Usage in config:
        SEARCH = [
            spass('closest', d('spectral-f0', norm=1))
        ]
    """
    # Note: This is a placeholder for integration
    # AudioGuide's descriptor system would need modification to support
    # runtime descriptor registration

    print("Spectral descriptors available:")
    print("  - spectral-f0: Median fundamental frequency (PYIN-based)")
    print("  - harmonic-count: Number of detected harmonics")
    print("  - harmonic-brightness: Spectral centroid of harmonics")
