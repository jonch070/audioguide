############################################################################
## This software is distributed for free, without warranties of any kind. ##
## Spectral reconstruction extensions for AudioGuide                      ##
############################################################################

"""
Spectral Analysis Module for AudioGuide

Provides harmonic series extraction and time-varying amplitude envelope
analysis for spectral reconstruction synthesis approach.

Key functions:
- extract_all_spectral_peaks: Direct FFT peak detection (no pitch estimation)
- group_peaks_into_harmonic_series: Separate polyphonic material into voices
- extract_partial_envelopes: Time-varying amplitude envelopes per partial
- extract_harmonic_series_fft: Extract fundamental + harmonics via FFT peak picking
- f0_pyin: Improved pitch detection using PYIN (fallback to basic detection)
"""

import numpy as np
from scipy.signal import butter, filtfilt, hilbert, find_peaks

# Try to import librosa for PYIN, but don't require it
try:
    import librosa
    HAS_LIBROSA = True
except ImportError:
    HAS_LIBROSA = False
    print("Warning: librosa not available. PYIN pitch detection disabled.")


def extract_harmonic_series_fft(audio, sr, f0, n_harmonics=16, tolerance_cents=50):
    """
    Extract harmonic partials using FFT-based peak picking.

    Args:
        audio: Audio signal (numpy array)
        sr: Sample rate
        f0: Fundamental frequency in Hz
        n_harmonics: Number of harmonics to extract (default 16)
        tolerance_cents: Frequency tolerance in cents (default 50)

    Returns:
        List of (frequency, amplitude) tuples for each detected harmonic
    """
    if f0 <= 0 or np.isnan(f0):
        return []

    # Compute FFT
    fft = np.fft.rfft(audio)
    freqs = np.fft.rfftfreq(len(audio), 1/sr)
    # Normalize magnitude by length to get amplitude-like values
    magnitude = np.abs(fft) * 2.0 / len(audio)

    partials = []

    # For each expected harmonic
    for h in range(1, n_harmonics + 1):
        target_freq = f0 * h

        # Frequency tolerance (50 cents ≈ 3% of frequency)
        freq_tolerance = target_freq * (2 ** (tolerance_cents / 1200) - 1)

        # Find spectral peak near target frequency
        mask = (freqs >= target_freq - freq_tolerance) & \
               (freqs <= target_freq + freq_tolerance)

        if np.any(mask):
            # Find peak in this region
            region_mags = magnitude[mask]
            if len(region_mags) > 0:
                peak_idx = np.argmax(region_mags)
                actual_freq = freqs[mask][peak_idx]
                actual_amp = region_mags[peak_idx]

                # Only include if amplitude is significant
                if actual_amp > np.max(magnitude) * 0.001:  # 0.1% of max
                    partials.append((actual_freq, actual_amp))

    return partials


def extract_partial_envelopes(audio, sr, partials, hop_ms=10):
    """
    Extract time-varying amplitude envelopes for each partial.

    Args:
        audio: Audio signal (numpy array)
        sr: Sample rate
        partials: List of (frequency, amplitude) tuples
        hop_ms: Envelope sampling interval in milliseconds (default 10ms)

    Returns:
        Dictionary {freq: envelope_array} where envelope_array is amplitude over time
    """
    envelopes = {}
    hop_samples = int(sr * hop_ms / 1000.0)

    for freq, amp in partials:
        try:
            # Bandpass filter around this frequency (±5%)
            nyquist = sr / 2
            low = max(10, freq * 0.95) / nyquist
            high = min(nyquist - 10, freq * 1.05) / nyquist

            # Ensure valid filter parameters
            if low >= high or low <= 0 or high >= 1.0:
                envelopes[freq] = np.array([amp])
                continue

            b, a = butter(4, [low, high], btype='band')
            filtered = filtfilt(b, a, audio)

            # Extract envelope using Hilbert transform
            analytic_signal = hilbert(filtered)
            envelope = np.abs(analytic_signal)

            # Downsample envelope
            envelope_downsampled = envelope[::hop_samples]

            envelopes[freq] = envelope_downsampled

        except Exception as e:
            # If filtering fails, use constant amplitude
            envelopes[freq] = np.array([amp])

    return envelopes


def f0_pyin(audio, sr, fmin=80, fmax=2000):
    """
    Improved pitch detection using Probabilistic YIN (PYIN).

    Args:
        audio: Audio signal (numpy array)
        sr: Sample rate
        fmin: Minimum frequency to detect (default 80 Hz)
        fmax: Maximum frequency to detect (default 2000 Hz)

    Returns:
        (f0_array, confidence_array) tuple
        - f0_array: Fundamental frequency over time (NaN for unvoiced)
        - confidence_array: Confidence scores (0-1)

    Falls back to simple zero-crossing method if librosa unavailable.
    """
    if HAS_LIBROSA:
        try:
            f0, voiced_flag, voiced_probs = librosa.pyin(
                audio,
                fmin=fmin,
                fmax=fmax,
                sr=sr,
                frame_length=2048
            )
            return f0, voiced_probs
        except Exception as e:
            print(f"PYIN failed: {e}, falling back to simple method")

    # Fallback: simple zero-crossing based pitch detection
    return _simple_f0_detection(audio, sr, fmin, fmax)


def _simple_f0_detection(audio, sr, fmin, fmax):
    """
    Simple zero-crossing based pitch detection (fallback).
    """
    # Basic zero crossing rate in sliding windows
    frame_length = 2048
    hop_length = 512

    n_frames = 1 + (len(audio) - frame_length) // hop_length
    f0_array = np.zeros(n_frames)
    confidence_array = np.zeros(n_frames)

    for i in range(n_frames):
        start = i * hop_length
        end = start + frame_length
        frame = audio[start:end]

        # Zero crossing rate
        zero_crossings = np.sum(np.abs(np.diff(np.sign(frame)))) / 2

        # Estimate period
        if zero_crossings > 0:
            period = len(frame) / zero_crossings
            freq = sr / period

            if fmin <= freq <= fmax:
                f0_array[i] = freq
                confidence_array[i] = 0.5  # Arbitrary confidence
            else:
                f0_array[i] = np.nan
                confidence_array[i] = 0.0
        else:
            f0_array[i] = np.nan
            confidence_array[i] = 0.0

    return f0_array, confidence_array


def get_median_f0(audio, sr, fmin=80, fmax=2000, confidence_threshold=0.3):
    """
    Get the median fundamental frequency for an audio segment.

    Args:
        audio: Audio signal
        sr: Sample rate
        fmin: Minimum frequency
        fmax: Maximum frequency
        confidence_threshold: Minimum confidence to include in median

    Returns:
        Median f0 (Hz) or 0.0 if no pitch detected
    """
    f0_array, confidence = f0_pyin(audio, sr, fmin, fmax)

    # Filter by confidence and remove NaN
    valid_mask = (confidence >= confidence_threshold) & ~np.isnan(f0_array)
    valid_f0 = f0_array[valid_mask]

    if len(valid_f0) > 0:
        return np.median(valid_f0)
    else:
        return 0.0


def extract_all_spectral_peaks(audio, sr, fmin=80, fmax=5000, min_amplitude_ratio=0.01, max_peaks=16):
    """
    Extract all significant spectral peaks without pitch detection.

    This method is more robust for spectral reconstruction as it doesn't
    rely on potentially unreliable pitch detection algorithms.

    Args:
        audio: Audio signal
        sr: Sample rate
        fmin: Minimum frequency to consider (Hz)
        fmax: Maximum frequency to consider (Hz)
        min_amplitude_ratio: Minimum peak amplitude relative to max (default 0.01 = 1%)
        max_peaks: Maximum number of peaks to return

    Returns:
        List of (frequency, amplitude) tuples sorted by amplitude (descending)
    """
    # Compute FFT
    fft = np.fft.rfft(audio)
    freqs = np.fft.rfftfreq(len(audio), 1/sr)
    # Normalize magnitude by length to get amplitude-like values
    # This ensures segments of different lengths have comparable amplitudes
    magnitude = np.abs(fft) * 2.0 / len(audio)

    # Filter to frequency range
    freq_mask = (freqs >= fmin) & (freqs <= fmax)
    freqs_filtered = freqs[freq_mask]
    mag_filtered = magnitude[freq_mask]

    if len(mag_filtered) == 0:
        return []

    # Find local peaks
    peaks, properties = find_peaks(mag_filtered, height=0)

    if len(peaks) == 0:
        return []

    # Filter by amplitude threshold
    max_magnitude = np.max(mag_filtered)
    threshold = max_magnitude * min_amplitude_ratio

    significant_peaks = []
    for peak_idx in peaks:
        amp = mag_filtered[peak_idx]
        if amp >= threshold:
            freq = freqs_filtered[peak_idx]
            significant_peaks.append((freq, amp))

    # Sort by amplitude (descending) and take top max_peaks
    significant_peaks.sort(key=lambda x: x[1], reverse=True)

    return significant_peaks[:max_peaks]


def compute_spectral_complexity(audio, sr, fmin=80, fmax=5000):
    """
    Compute spectral complexity metric (0-1) based on spectral peak distribution.
    
    Higher values indicate more complex spectra (polyphonic, dissonant, etc.)
    Lower values indicate simpler spectra (single notes, harmonic series)
    
    Args:
        audio: Audio signal
        sr: Sample rate
        fmin: Minimum frequency to consider
        fmax: Maximum frequency to consider
    
    Returns:
        Complexity score between 0 (simple) and 1 (complex)
    """
    # Compute FFT
    fft = np.fft.rfft(audio)
    freqs = np.fft.rfftfreq(len(audio), 1/sr)
    magnitude = np.abs(fft)
    
    # Filter to frequency range
    freq_mask = (freqs >= fmin) & (freqs <= fmax)
    freqs_filtered = freqs[freq_mask]
    mag_filtered = magnitude[freq_mask]
    
    if len(mag_filtered) == 0:
        return 0.5  # Default to medium complexity
    
    # Normalize magnitudes
    mag_normalized = mag_filtered / np.max(mag_filtered)
    
    # Find significant peaks
    peaks, _ = find_peaks(mag_filtered, height=0)
    
    if len(peaks) < 2:
        return 0.1  # Very simple - single prominent frequency
    
    # Calculate metrics:
    # 1. Number of peaks relative to frequency span
    peak_density = len(peaks) / len(freqs_filtered) * 1000
    
    # 2. Distribution entropy - how spread out the energy is
    # Lower entropy = energy concentrated in few peaks
    # Higher entropy = energy spread across many frequencies
    hist, _ = np.histogram(mag_normalized, bins=10, range=(0, 1))
    hist = hist / np.sum(hist)  # Normalize
    hist = hist[hist > 0]  # Remove zeros for log
    entropy = -np.sum(hist * np.log2(hist))
    max_entropy = np.log2(10)  # Maximum possible entropy for 10 bins
    entropy_normalized = entropy / max_entropy
    
    # 3. Peak spacing - are peaks harmonically related or random?
    peak_freqs = freqs_filtered[peaks]
    if len(peak_freqs) > 1:
        # Check for harmonic relationships (peaks at integer ratios)
        # If peaks are at harmonic ratios, lower complexity
        harmonic_count = 0
        for i, f1 in enumerate(peak_freqs):
            for f2 in peak_freqs[i+1:]:
                if f1 > 0:
                    ratio = f2 / f1
                    # Check if close to integer (harmonic)
                    nearest_int = round(ratio)
                    if abs(ratio - nearest_int) < 0.1:
                        harmonic_count += 1
        harmonic_ratio = harmonic_count / max(1, len(peaks) * (len(peaks) - 1) / 2)
    else:
        harmonic_ratio = 1.0
    
    # Combined complexity metric
    # More peaks + higher entropy + less harmonic = more complex
    complexity = (peak_density * 0.3 + entropy_normalized * 0.4 + (1 - harmonic_ratio) * 0.3)
    
    # Clamp to 0-1 range
    return min(1.0, max(0.0, complexity))


def adapt_partial_count(audio, sr, base_max=8, min_partials=2, max_partials=32, 
                        complexity_threshold=0.3, fmin=80, fmax=5000):
    """
    Adaptively determine optimal number of partials based on spectral complexity.
    
    For simple spectra (single notes), fewer partials are needed.
    For complex spectra (chords, polyphony), more partials are needed.
    
    Args:
        audio: Audio signal
        sr: Sample rate
        base_max: Base maximum partials (used as reference)
        min_partials: Minimum partials to use
        max_partials: Maximum partials to use
        complexity_threshold: Threshold for complexity scaling (0-1)
        fmin: Minimum frequency for analysis
        fmax: Maximum frequency for analysis
    
    Returns:
        Recommended number of partials
    """
    complexity = compute_spectral_complexity(audio, sr, fmin, fmax)
    
    # Scale partials based on complexity
    # complexity 0 -> use base_max
    # complexity 1 -> use max_partials
    # complexity near threshold -> use base_max
    
    if complexity < complexity_threshold:
        # Simple spectrum - use base or fewer
        partials = base_max
    else:
        # Complex spectrum - scale up
        scale = (complexity - complexity_threshold) / (1.0 - complexity_threshold)
        partials = int(base_max + scale * (max_partials - base_max))
    
    # Clamp to bounds
    return max(min_partials, min(max_partials, partials))


def group_peaks_into_harmonic_series(peaks, tolerance_cents=50, min_harmonics=3, max_voices=8):
    """
    Group spectral peaks into harmonic series to identify individual notes/voices.

    This enables separation of polyphonic material into constituent notes by
    identifying which peaks form harmonic relationships.

    Args:
        peaks: List of (frequency, amplitude) tuples from extract_all_spectral_peaks
        tolerance_cents: Frequency matching tolerance in cents (default 50)
        min_harmonics: Minimum number of harmonics required to identify a voice (default 3)
        max_voices: Maximum number of voices to identify (default 8)

    Returns:
        List of voice dictionaries, each containing:
        - 'f0': Fundamental frequency (Hz)
        - 'note_name': Musical note name
        - 'harmonics': List of (freq, amp) tuples for this voice's harmonics
        - 'harmonic_numbers': List of harmonic numbers (1=fundamental, 2=octave, etc)
        - 'strength': Combined amplitude of all harmonics
    """
    if not peaks or len(peaks) == 0:
        return []

    def cents_difference(f1, f2):
        """Calculate frequency difference in cents"""
        if f1 <= 0 or f2 <= 0:
            return float('inf')
        return abs(1200 * np.log2(f2 / f1))

    def freq_to_note_name(freq):
        """Convert frequency to note name (e.g., 440 Hz -> A4)"""
        if freq <= 0:
            return "unknown"
        A4 = 440.0
        C0 = A4 * pow(2, -4.75)
        h = round(12 * np.log2(freq / C0))
        octave = h // 12
        n = h % 12
        note_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        return note_names[n] + str(octave)

    # Sort peaks by amplitude (strongest first)
    sorted_peaks = sorted(peaks, key=lambda x: x[1], reverse=True)

    # Track which peaks have been assigned to voices
    unassigned_peaks = list(range(len(sorted_peaks)))
    voices = []

    # Try to build harmonic series starting from each strong peak as potential fundamental
    for potential_f0_idx in range(len(sorted_peaks)):
        if potential_f0_idx not in unassigned_peaks:
            continue  # Already assigned to a voice

        if len(voices) >= max_voices:
            break  # Found enough voices

        potential_f0, f0_amp = sorted_peaks[potential_f0_idx]

        # Search for harmonics of this potential fundamental
        harmonics = []
        harmonic_numbers = []

        # Check harmonics 1 through 8
        for n in range(1, 9):
            expected_freq = potential_f0 * n

            # Find closest peak to expected harmonic frequency
            best_match_idx = None
            best_match_cents = float('inf')

            for peak_idx in unassigned_peaks:
                peak_freq, peak_amp = sorted_peaks[peak_idx]
                cents_diff = cents_difference(expected_freq, peak_freq)

                if cents_diff < best_match_cents and cents_diff <= tolerance_cents:
                    best_match_idx = peak_idx
                    best_match_cents = cents_diff

            if best_match_idx is not None:
                harmonics.append(sorted_peaks[best_match_idx])
                harmonic_numbers.append(n)

        # Only accept if we found enough harmonics
        if len(harmonics) >= min_harmonics:
            # Calculate voice strength (sum of harmonic amplitudes)
            strength = sum(amp for _, amp in harmonics)

            voice = {
                'f0': potential_f0,
                'note_name': freq_to_note_name(potential_f0),
                'harmonics': harmonics,
                'harmonic_numbers': harmonic_numbers,
                'strength': strength
            }
            voices.append(voice)

            # Mark these peaks as assigned
            for freq, amp in harmonics:
                for idx in unassigned_peaks[:]:
                    if sorted_peaks[idx][0] == freq:
                        unassigned_peaks.remove(idx)
                        break

    # Sort voices by strength (loudest first)
    voices.sort(key=lambda v: v['strength'], reverse=True)

    return voices


def analyze_segment_spectrum(audio, sr, fmin=80, fmax=2000, n_harmonics=16):
    """
    Complete spectral analysis of an audio segment.

    Args:
        audio: Audio signal
        sr: Sample rate
        fmin: Minimum f0 to detect
        fmax: Maximum f0 to detect
        n_harmonics: Number of harmonics to extract

    Returns:
        Dictionary with:
        - 'f0': Median fundamental frequency
        - 'harmonics': List of (freq, amp) tuples
        - 'envelopes': Dict of {freq: envelope_array}
    """
    # NEW APPROACH: Extract all spectral peaks directly without pitch detection
    # This is much more robust for spectral reconstruction
    harmonics = extract_all_spectral_peaks(
        audio, sr,
        fmin=fmin,
        fmax=fmax,
        min_amplitude_ratio=0.01,  # 1% threshold
        max_peaks=n_harmonics
    )

    # Estimate f0 from lowest peak (optional, for reference only)
    if len(harmonics) > 0:
        f0 = harmonics[-1][0]  # Lowest frequency peak (harmonics sorted by amplitude)
        # Try to find actual fundamental by looking for lowest frequency component
        freqs = [h[0] for h in harmonics]
        f0 = min(freqs) if freqs else 0.0
    else:
        f0 = 0.0

    # Extract time-varying envelopes
    envelopes = extract_partial_envelopes(audio, sr, harmonics)

    return {
        'f0': f0,
        'harmonics': harmonics,
        'envelopes': envelopes
    }
