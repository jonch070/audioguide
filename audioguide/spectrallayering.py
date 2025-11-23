############################################################################
## This software is distributed for free, without warranties of any kind. ##
## Spectral reconstruction extensions for AudioGuide                      ##
############################################################################

"""
Spectral Layering Module for AudioGuide

Implements spectral reconstruction synthesis by matching corpus sounds
to individual partials/harmonics of the target sound.

Key approach:
- Extract target's harmonic series (fundamental + harmonics)
- Match corpus sounds by natural frequency (NO transposition)
- Compute gain adjustments to match partial amplitudes
- Layer multiple corpus sounds to recreate target spectrum
"""

import numpy as np
import soundfile as sf
import audioguide.spectralanalysis as spectralanalysis


def freq_to_cents(freq1, freq2):
    """
    Calculate interval in cents between two frequencies.

    Args:
        freq1, freq2: Frequencies in Hz

    Returns:
        Interval in cents (1200 cents = 1 octave)
    """
    if freq1 <= 0 or freq2 <= 0:
        return float('inf')
    return 1200 * np.log2(freq2 / freq1)


def freq_to_midi(freq):
    """Convert frequency to MIDI note number."""
    if freq <= 0:
        return -1
    return 69 + 12 * np.log2(freq / 440.0)


def midi_to_note_name(midi):
    """Convert MIDI note number to note name."""
    note_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    return note_names[int(round(midi)) % 12]


# Scale definitions (semitone intervals from root)
SCALES = {
    'major': [0, 2, 4, 5, 7, 9, 11],
    'minor': [0, 2, 3, 5, 7, 8, 10],
    'dorian': [0, 2, 3, 5, 7, 9, 10],
    'phrygian': [0, 1, 3, 5, 7, 8, 10],
    'lydian': [0, 2, 4, 6, 7, 9, 11],
    'mixolydian': [0, 2, 4, 5, 7, 9, 10],
    'chromatic': list(range(12))  # All notes
}

# Krumhansl-Schmuckler key profiles for major and minor keys
# Higher values = stronger presence in the key
KEY_PROFILES = {
    'major': [6.35, 2.23, 3.48, 2.33, 4.38, 4.09, 2.52, 5.19, 2.39, 3.66, 2.29, 2.88],
    'minor': [6.33, 2.68, 3.52, 5.38, 2.60, 3.53, 2.54, 4.75, 3.98, 2.69, 3.34, 3.17]
}


def freq_in_key(freq, key_root='C', scale_type='major'):
    """
    Check if a frequency's closest note belongs to a key.

    Args:
        freq: Frequency in Hz
        key_root: Root note ('C', 'D#', etc.)
        scale_type: 'major', 'minor', 'dorian', etc.

    Returns:
        True if frequency's note is in the key
    """
    # Convert frequency to MIDI note
    midi = freq_to_midi(freq)
    if midi < 0:
        return False

    # Get note class (0-11, where C=0)
    note_class = int(round(midi)) % 12

    # Get root note class
    note_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    try:
        root_class = note_names.index(key_root)
    except ValueError:
        # Invalid root, allow all notes
        return True

    # Get scale intervals
    if scale_type not in SCALES:
        # Unknown scale, allow all notes
        return True
    scale_intervals = SCALES[scale_type]

    # Check if note belongs to scale
    scale_notes = [(root_class + interval) % 12 for interval in scale_intervals]
    return note_class in scale_notes


def detect_key_from_frequencies(frequencies, amplitudes=None):
    """
    Detect the musical key from a list of frequencies using Krumhansl-Schmuckler algorithm.

    Args:
        frequencies: List/array of frequencies in Hz
        amplitudes: Optional list/array of amplitudes (weights). If None, all frequencies weighted equally.

    Returns:
        Tuple of (key_root, scale_type) e.g. ('C', 'major') or ('G#', 'minor')
    """
    if len(frequencies) == 0:
        return ('C', 'major')  # Default fallback

    # Build pitch class histogram (12 semitones)
    pitch_class_hist = np.zeros(12)

    for i, freq in enumerate(frequencies):
        midi = freq_to_midi(freq)
        if midi < 0:
            continue
        note_class = int(round(midi)) % 12
        weight = amplitudes[i] if amplitudes is not None and i < len(amplitudes) else 1.0
        pitch_class_hist[note_class] += weight

    # Normalize histogram
    if pitch_class_hist.sum() > 0:
        pitch_class_hist = pitch_class_hist / pitch_class_hist.sum()

    # Try all 24 keys (12 major + 12 minor) using Krumhansl-Schmuckler correlation
    note_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    best_correlation = -1
    best_key_root = 'C'
    best_scale_type = 'major'

    for scale_type in ['major', 'minor']:
        profile = np.array(KEY_PROFILES[scale_type])

        for root_idx in range(12):
            # Rotate profile to match this root
            rotated_profile = np.roll(profile, root_idx)

            # Compute Pearson correlation
            if pitch_class_hist.std() > 0 and rotated_profile.std() > 0:
                correlation = np.corrcoef(pitch_class_hist, rotated_profile)[0, 1]

                if correlation > best_correlation:
                    best_correlation = correlation
                    best_key_root = note_names[root_idx]
                    best_scale_type = scale_type

    return (best_key_root, best_scale_type)


def find_corpus_by_frequency(corpus_segments, target_freq, tolerance_cents=50,
                            target_duration_sec=None, duration_tolerance_sec=None,
                            corpus_usage_tracker=None, no_repeat=False,
                            time_sparsity_sec=None, current_time_sec=0,
                            key_aware=False, key_root='C', scale_type='major'):
    """
    Find corpus sounds whose fundamental frequency matches target frequency.

    Args:
        corpus_segments: List of corpus segment objects
        target_freq: Target frequency in Hz
        tolerance_cents: Matching tolerance in cents (default 50)
        target_duration_sec: Target segment duration in seconds (optional)
        duration_tolerance_sec: Duration matching tolerance in seconds (optional)
                               If provided, only match corpus files within ±tolerance of target duration
        corpus_usage_tracker: Dictionary tracking corpus file usage (key: filename, value: last use time)
        no_repeat: If True, exclude any previously used corpus files
        time_sparsity_sec: Minimum seconds before same file can be reused
        current_time_sec: Current position in target timeline
        key_aware: If True, filter corpus files to match musical key
        key_root: Root note of key ('C', 'D#', etc.)
        scale_type: Scale type ('major', 'minor', 'dorian', etc.)

    Returns:
        List of (segment, freq_diff_cents) tuples for matching segments
    """
    matches = []

    for seg in corpus_segments:
        # Get corpus segment's fundamental frequency
        # Assumes seg has f0 descriptor - we'll need to ensure this is computed
        if hasattr(seg, 'spectral_f0'):
            corpus_f0 = seg.spectral_f0
        elif hasattr(seg.desc, 'get'):
            # Try to get from descriptor system
            try:
                corpus_f0 = seg.desc.get('f0-seg', 0)
            except:
                corpus_f0 = 0
        else:
            corpus_f0 = 0

        if corpus_f0 <= 0:
            continue

        # Calculate frequency difference in cents
        freq_diff = abs(freq_to_cents(corpus_f0, target_freq))

        if freq_diff > tolerance_cents:
            continue

        # Optional key-aware filtering
        if key_aware:
            if not freq_in_key(corpus_f0, key_root=key_root, scale_type=scale_type):
                # Corpus note not in target key, skip it
                continue

        # Optional duration filtering
        if target_duration_sec is not None and duration_tolerance_sec is not None:
            corpus_duration = seg.segmentDurationSec
            duration_diff = abs(corpus_duration - target_duration_sec)

            if duration_diff > duration_tolerance_sec:
                # Skip this corpus file - duration is outside tolerance
                continue

        # No-repeat and time sparsity filtering
        if corpus_usage_tracker is not None:
            corpus_filename = seg.filename

            if no_repeat and corpus_filename in corpus_usage_tracker:
                # This file has been used before, skip it completely
                continue

            if time_sparsity_sec is not None and corpus_filename in corpus_usage_tracker:
                last_use_time = corpus_usage_tracker[corpus_filename]
                time_since_last_use = current_time_sec - last_use_time

                if time_since_last_use < time_sparsity_sec:
                    # Too soon to reuse this file
                    continue

        matches.append((seg, freq_diff))

    # Sort by frequency difference (closest first)
    matches.sort(key=lambda x: x[1])

    return matches


def compute_gain_adjustment(target_amp, corpus_amp):
    """
    Compute gain in dB needed to adjust corpus amplitude to match target.

    Args:
        target_amp: Target amplitude (linear)
        corpus_amp: Corpus amplitude (linear)

    Returns:
        Gain adjustment in dB
    """
    if corpus_amp <= 0:
        return -120.0  # Very quiet

    ratio = target_amp / corpus_amp
    gain_db = 20 * np.log10(ratio) if ratio > 0 else -120.0

    # Clamp to reasonable range
    return np.clip(gain_db, -60.0, 24.0)


def compute_gain_envelope(target_envelope, corpus_envelope, time_offset=0, duration_sec=1.0):
    """
    Compute time-varying gain envelope to match target amplitude evolution.

    Args:
        target_envelope: Array of target amplitudes over time
        corpus_envelope: Array of corpus amplitudes over time
        time_offset: Start time offset in seconds
        duration_sec: Total duration in seconds

    Returns:
        List of (time, gain_db) tuples
    """
    envelope_points = []

    # Match lengths by interpolation if needed
    target_len = len(target_envelope)
    corpus_len = len(corpus_envelope)

    if target_len == 0 or corpus_len == 0:
        return [(time_offset, 0.0)]

    # Interpolate corpus to match target length
    if corpus_len != target_len:
        corpus_resampled = np.interp(
            np.linspace(0, corpus_len-1, target_len),
            np.arange(corpus_len),
            corpus_envelope
        )
    else:
        corpus_resampled = corpus_envelope

    # Compute gain at each time point
    # Sample every 10 points to avoid too many automation points
    sample_rate = max(1, target_len // 50)  # Max 50 points per envelope

    for i in range(0, target_len, sample_rate):
        t_amp = target_envelope[i]
        c_amp = corpus_resampled[i]

        gain_db = compute_gain_adjustment(t_amp, c_amp)
        time_sec = time_offset + (i / target_len) * duration_sec  # Scale by duration

        envelope_points.append((time_sec, gain_db))

    return envelope_points


def spectral_layering_match(target_segment, corpus_segments, AnalInterface,
                            tolerance_cents=50, max_partials=8, min_amplitude_ratio=0.01,
                            enable_polyphonic=False, polyphonic_tolerance_cents=50,
                            polyphonic_min_harmonics=3, polyphonic_max_voices=4,
                            duration_tolerance_sec=None,
                            corpus_usage_tracker=None, no_repeat=False,
                            time_sparsity_sec=None, current_time_sec=0,
                            key_aware=False, key_root='C', scale_type='major'):
    """
    Match corpus sounds to target segment's harmonic partials.

    Core spectral reconstruction algorithm:
    1. Extract target's harmonic series
    2. For each strong partial, find corpus sound with matching f0
    3. Compute gain adjustment needed
    4. Return layered selection

    Args:
        target_segment: Target segment object
        corpus_segments: List of available corpus segments
        AnalInterface: AudioGuide analysis interface
        tolerance_cents: Frequency matching tolerance (default 50 cents)
        max_partials: Maximum partials to match (default 8)
        min_amplitude_ratio: Minimum partial amplitude (relative to max) to include
        enable_polyphonic: Enable polyphonic analysis (grouping peaks into voices)
        polyphonic_tolerance_cents: Tolerance for harmonic grouping (default 50 cents)
        polyphonic_min_harmonics: Minimum harmonics to identify a voice (default 3)
        polyphonic_max_voices: Maximum voices to identify (default 4)
        duration_tolerance_sec: Duration matching tolerance in seconds (optional)
                               Only match corpus files within ±tolerance of target duration
                               Use when SPECTRAL_TRIM_TO_TARGET=False to prevent mismatched durations
        corpus_usage_tracker: Dictionary tracking corpus file usage (modified in place)
        no_repeat: If True, never reuse any corpus file (default False)
        time_sparsity_sec: Minimum seconds before same corpus file can be reused (optional)
        current_time_sec: Current position in target timeline (for time sparsity tracking)
        key_aware: If True, filter corpus files to match musical key
        key_root: Root note of key ('C', 'D#', etc.)
        scale_type: Scale type ('major', 'minor', 'dorian', etc.)

    Returns:
        List of dictionaries:
        [{
            'corpus_segment': segment object,
            'target_partial_freq': float,
            'target_partial_index': int,  # 1=fundamental, 2=2nd harmonic, etc.
            'gain_db': float,
            'gain_envelope': [(time, gain_db), ...],
            'match_quality': float (0-1),
            'voice_id': int (polyphonic mode only),
            'voice_f0': float (polyphonic mode only)
        }, ...]
    """

    # Get target audio data - load directly using soundfile
    audio_data, sr = sf.read(target_segment.filename)

    # Convert to mono if stereo
    if len(audio_data.shape) > 1:
        audio_data = audio_data.mean(axis=1)

    # Extract segment
    start_sample = int(target_segment.segmentStartSec * sr)
    end_sample = int((target_segment.segmentStartSec + target_segment.segmentDurationSec) * sr)
    target_audio = audio_data[start_sample:end_sample]

    selected_matches = []

    if enable_polyphonic:
        # POLYPHONIC MODE: Detect multiple voices/notes in the segment

        # Extract all spectral peaks
        all_peaks = spectralanalysis.extract_all_spectral_peaks(
            target_audio, sr, fmin=80, fmax=2000,
            min_amplitude_ratio=min_amplitude_ratio, max_peaks=32
        )

        if len(all_peaks) == 0:
            return []

        # Group peaks into harmonic series (voices)
        voices = spectralanalysis.group_peaks_into_harmonic_series(
            all_peaks,
            tolerance_cents=polyphonic_tolerance_cents,
            min_harmonics=polyphonic_min_harmonics,
            max_voices=polyphonic_max_voices
        )

        if len(voices) == 0:
            # No voices identified - fall back to monophonic mode
            print(f"  Polyphonic analysis found no voices - falling back to monophonic mode")
            enable_polyphonic = False
        else:
            # Process each identified voice
            print(f"  Polyphonic analysis identified {len(voices)} voice(s) in segment")

            for voice_idx, voice in enumerate(voices, start=1):
                voice_f0 = voice['f0']
                voice_harmonics = voice['harmonics']
                voice_note = voice['note_name']

                print(f"    Voice {voice_idx}: {voice_note} ({voice_f0:.1f} Hz) with {len(voice_harmonics)} harmonics")

                # Extract envelope for this voice's harmonics
                # Average envelope across all harmonics of this voice
                voice_envelopes = {}
                for freq, amp in voice_harmonics[:max_partials]:
                    try:
                        voice_envelopes[freq] = spectralanalysis.compute_partial_envelopes(
                            {freq: amp}, target_audio, sr
                        ).get(freq, np.array([amp]))
                    except:
                        voice_envelopes[freq] = np.array([amp])

                # Normalize amplitudes within this voice
                voice_max_amp = max([amp for freq, amp in voice_harmonics])

                # Match each harmonic of this voice
                for partial_idx, (partial_freq, partial_amp) in enumerate(voice_harmonics[:max_partials], start=1):

                    # Skip very quiet partials
                    if partial_amp < voice_max_amp * min_amplitude_ratio:
                        continue

                    # Find corpus sounds matching this partial frequency
                    candidates = find_corpus_by_frequency(corpus_segments, partial_freq, tolerance_cents,
                                                         target_duration_sec=target_segment.segmentDurationSec,
                                                         duration_tolerance_sec=duration_tolerance_sec,
                                                         corpus_usage_tracker=corpus_usage_tracker,
                                                         no_repeat=no_repeat,
                                                         time_sparsity_sec=time_sparsity_sec,
                                                         current_time_sec=current_time_sec,
                                                         key_aware=key_aware,
                                                         key_root=key_root,
                                                         scale_type=scale_type)

                    if len(candidates) == 0:
                        continue

                    # Select best match (closest frequency)
                    best_segment, freq_diff = candidates[0]

                    # Update usage tracker
                    if corpus_usage_tracker is not None:
                        corpus_usage_tracker[best_segment.filename] = current_time_sec

                    # Compute gain adjustment
                    try:
                        corpus_data, corpus_sr = sf.read(best_segment.filename)
                        if len(corpus_data.shape) > 1:
                            corpus_data = corpus_data.mean(axis=1)

                        cps_start = int(best_segment.segmentStartSec * corpus_sr)
                        cps_end = int((best_segment.segmentStartSec + best_segment.segmentDurationSec) * corpus_sr)
                        corpus_audio = corpus_data[cps_start:cps_end]

                        corpus_spectrum = spectralanalysis.analyze_segment_spectrum(
                            corpus_audio, corpus_sr, fmin=80, fmax=2000, n_harmonics=1
                        )

                        if len(corpus_spectrum['harmonics']) > 0:
                            corpus_fundamental_amp = corpus_spectrum['harmonics'][0][1]
                        else:
                            corpus_fundamental_amp = 1.0
                    except Exception as e:
                        print(f"Warning: Could not analyze corpus segment: {e}")
                        corpus_fundamental_amp = 1.0

                    base_gain_db = compute_gain_adjustment(partial_amp, corpus_fundamental_amp)

                    # Compute envelope
                    if partial_freq in voice_envelopes and len(voice_envelopes[partial_freq]) > 1:
                        target_env = voice_envelopes[partial_freq]

                        if corpus_spectrum['harmonics'] and corpus_spectrum['harmonics'][0][0] in corpus_spectrum['envelopes']:
                            corpus_env = corpus_spectrum['envelopes'][corpus_spectrum['harmonics'][0][0]]
                        else:
                            corpus_env = np.array([corpus_fundamental_amp])

                        gain_envelope = compute_gain_envelope(
                            target_env, corpus_env,
                            time_offset=target_segment.segmentStartSec,
                            duration_sec=target_segment.segmentDurationSec
                        )
                    else:
                        gain_envelope = [(target_segment.segmentStartSec, base_gain_db)]

                    match_quality = 1.0 - (freq_diff / tolerance_cents) if tolerance_cents > 0 else 1.0
                    match_quality = np.clip(match_quality, 0.0, 1.0)

                    selected_matches.append({
                        'corpus_segment': best_segment,
                        'target_partial_freq': partial_freq,
                        'target_partial_index': partial_idx,
                        'gain_db': base_gain_db,
                        'gain_envelope': gain_envelope,
                        'match_quality': match_quality,
                        'voice_id': voice_idx,
                        'voice_f0': voice_f0,
                        'voice_note': voice_note
                    })

            return selected_matches

    # MONOPHONIC MODE (default or fallback)
    if not enable_polyphonic:
        # Analyze target spectrum
        spectrum = spectralanalysis.analyze_segment_spectrum(
            target_audio, sr, fmin=80, fmax=2000, n_harmonics=16
        )

        if spectrum['f0'] <= 0 or len(spectrum['harmonics']) == 0:
            # No pitch detected - fall back to standard matching
            return []

        target_harmonics = spectrum['harmonics']
        target_envelopes = spectrum['envelopes']

        # Normalize amplitudes
        max_amp = max([amp for freq, amp in target_harmonics])

        # Match each harmonic (prioritize lower harmonics)
        for partial_idx, (partial_freq, partial_amp) in enumerate(target_harmonics[:max_partials], start=1):

            # Skip very quiet partials
            if partial_amp < max_amp * min_amplitude_ratio:
                continue

            # Find corpus sounds matching this partial frequency
            candidates = find_corpus_by_frequency(corpus_segments, partial_freq, tolerance_cents,
                                                 target_duration_sec=target_segment.segmentDurationSec,
                                                 duration_tolerance_sec=duration_tolerance_sec,
                                                 corpus_usage_tracker=corpus_usage_tracker,
                                                 no_repeat=no_repeat,
                                                 time_sparsity_sec=time_sparsity_sec,
                                                 current_time_sec=current_time_sec,
                                                 key_aware=key_aware,
                                                 key_root=key_root,
                                                 scale_type=scale_type)

            if len(candidates) == 0:
                # No match found for this partial
                continue

            # Select best match (closest frequency)
            best_segment, freq_diff = candidates[0]

            # Update usage tracker
            if corpus_usage_tracker is not None:
                corpus_usage_tracker[best_segment.filename] = current_time_sec

            # Compute base gain adjustment
            # We need corpus amplitude - load audio and analyze
            try:
                # Load corpus audio
                corpus_data, corpus_sr = sf.read(best_segment.filename)
                if len(corpus_data.shape) > 1:
                    corpus_data = corpus_data.mean(axis=1)

                # Extract segment
                cps_start = int(best_segment.segmentStartSec * corpus_sr)
                cps_end = int((best_segment.segmentStartSec + best_segment.segmentDurationSec) * corpus_sr)
                corpus_audio = corpus_data[cps_start:cps_end]

                # Get corpus f0 and fundamental amplitude
                corpus_spectrum = spectralanalysis.analyze_segment_spectrum(
                    corpus_audio, corpus_sr, fmin=80, fmax=2000, n_harmonics=1
                )

                if len(corpus_spectrum['harmonics']) > 0:
                    corpus_fundamental_amp = corpus_spectrum['harmonics'][0][1]
                else:
                    corpus_fundamental_amp = 1.0
            except Exception as e:
                print(f"Warning: Could not analyze corpus segment: {e}")
                corpus_fundamental_amp = 1.0

            # Compute gain to match target partial amplitude
            base_gain_db = compute_gain_adjustment(partial_amp, corpus_fundamental_amp)

            # Compute time-varying gain envelope if we have envelope data
            if partial_freq in target_envelopes and len(target_envelopes[partial_freq]) > 1:
                target_env = target_envelopes[partial_freq]

                # For corpus envelope, use fundamental envelope or constant
                if corpus_spectrum['harmonics'] and corpus_spectrum['harmonics'][0][0] in corpus_spectrum['envelopes']:
                    corpus_env = corpus_spectrum['envelopes'][corpus_spectrum['harmonics'][0][0]]
                else:
                    corpus_env = np.array([corpus_fundamental_amp])

                gain_envelope = compute_gain_envelope(
                    target_env,
                    corpus_env,
                    time_offset=target_segment.segmentStartSec,
                    duration_sec=target_segment.segmentDurationSec
                )
            else:
                # Static gain
                gain_envelope = [(target_segment.segmentStartSec, base_gain_db)]

            # Match quality score (inverse of frequency difference)
            match_quality = 1.0 - (freq_diff / tolerance_cents) if tolerance_cents > 0 else 1.0
            match_quality = np.clip(match_quality, 0.0, 1.0)

            selected_matches.append({
                'corpus_segment': best_segment,
                'target_partial_freq': partial_freq,
                'target_partial_index': partial_idx,
                'gain_db': base_gain_db,
                'gain_envelope': gain_envelope,
                'match_quality': match_quality
            })

        return selected_matches


def create_spectral_output_events(spectral_matches, target_segment, AnalInterface):
    """
    Convert spectral matching results into AudioGuide output events.

    Args:
        spectral_matches: List of match dictionaries from spectral_layering_match
        target_segment: Target segment being reconstructed
        AnalInterface: Analysis interface

    Returns:
        List of output event data structures compatible with AudioGuide
    """
    output_events = []

    for match in spectral_matches:
        corpus_seg = match['corpus_segment']

        # Create event data structure
        event = {
            'corpus_segment': corpus_seg,
            'filename': corpus_seg.filename,
            'time': target_segment.segmentStartSec,
            'duration': target_segment.segmentDurationSec,
            'skip': corpus_seg.segmentStartSec,
            'gain_db': match['gain_db'],
            'gain_envelope': match['gain_envelope'],  # NEW: time-varying gain
            'transposition': 0.0,  # NO transposition per user preference
            'partial_index': match['target_partial_index'],
            'target_freq': match['target_partial_freq'],
            'match_quality': match['match_quality']
        }

        output_events.append(event)

    return output_events
