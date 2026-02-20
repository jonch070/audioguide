"""
FluCoMa Target Segmentation

This module provides functions to use FluCoMa CLI tools for target audio segmentation.
Unlike IRCAM's amplitude-based onset detection, FluCoMa offers multiple segmentation
strategies optimized for different types of musical material.

Available segmentation methods:
- noveltyslice: Detects spectral changes (good for detecting note changes, timbral shifts)
- ampslice: Amplitude-based onset detection (similar to IRCAM, but with different algorithm)
- onsetslice: Specialized onset detection (good for percussive material)
- transientslice: Transient detection (good for percussive attacks)

For melodic material like cello, noveltyslice is often the best choice as it detects
pitch changes and timbral shifts rather than just amplitude onsets.
"""

import os
import subprocess
import tempfile
import shutil


def segment_with_flucoma(audio_path, method='noveltyslice', **kwargs):
    """
    Segment an audio file using FluCoMa CLI tools.

    Args:
        audio_path: Path to audio file to segment
        method: Segmentation method ('noveltyslice', 'ampslice', 'onsetslice', 'transientslice')
        **kwargs: Method-specific parameters

    Returns:
        Path to segmentation file (text file with timestamps in seconds)

    Raises:
        RuntimeError: If FluCoMa CLI tools are not installed
        ValueError: If method is not recognized
    """

    # Check if FluCoMa CLI is available
    fluid_command = f'fluid-{method}'
    fluid_path = shutil.which(fluid_command)

    if not fluid_path:
        raise RuntimeError(
            f"FluCoMa CLI tool '{fluid_command}' not found in PATH. "
            "Install from: https://www.flucoma.org/download/"
        )

    # Create temporary output file path for slice indices
    # Don't pre-create the file - let FluCoMa create it
    indices_path = tempfile.mktemp(suffix='_indices.wav')

    # Build command based on method
    cmd = [
        fluid_path,
        '-source', audio_path,
        '-indices', indices_path
    ]

    # Add method-specific parameters
    if method == 'noveltyslice':
        # Novelty slice parameters (spectral change detection)
        algorithm = kwargs.get('algorithm', 0)  # 0=spectrum, 1=mfcc, 2=chroma
        threshold = kwargs.get('threshold', 0.5)  # Threshold (0-1)

        cmd.extend([
            '-algorithm', str(algorithm),
            '-threshold', str(threshold)
        ])

        # kernelsize: expects TWO values [inner, outer] for the kernel size
        # Default: [3, 5] - controls temporal smoothing of the novelty curve
        kernelsize = kwargs.get('kernelsize', None)
        if kernelsize is not None:
            if isinstance(kernelsize, (list, tuple)) and len(kernelsize) == 2:
                cmd.extend(['-kernelsize', str(kernelsize[0]), str(kernelsize[1])])
            else:
                raise ValueError("kernelsize must be a list/tuple of 2 integers [inner, outer]")

        # filtersize: expects TWO values [before, after] for smoothing filter
        # Default: [1, 3] - controls smoothing of the novelty curve
        filtersize = kwargs.get('filtersize', None)
        if filtersize is not None:
            if isinstance(filtersize, (list, tuple)) and len(filtersize) == 2:
                cmd.extend(['-filtersize', str(filtersize[0]), str(filtersize[1])])
            else:
                raise ValueError("filtersize must be a list/tuple of 2 integers [before, after]")

        # minslicelength: minimum slice length in samples
        # Default: not specified (no minimum)
        minSliceLength = kwargs.get('minSliceLength', None)
        if minSliceLength is not None:
            cmd.extend(['-minslicelength', str(minSliceLength)])

        # fftsettings: expects THREE values [fftsize, hopsize, windowsize]
        # Default: depends on audio, typically [1024, -1, -1] where -1 = auto
        fftsettings = kwargs.get('fftsettings', None)
        if fftsettings is not None:
            if isinstance(fftsettings, (list, tuple)) and len(fftsettings) == 3:
                cmd.extend(['-fftsettings', str(fftsettings[0]), str(fftsettings[1]), str(fftsettings[2])])
            else:
                raise ValueError("fftsettings must be a list/tuple of 3 integers [fftsize, hopsize, windowsize]")

    elif method == 'ampslice':
        # Amplitude slice parameters (onset detection)
        fastRampUpTime = kwargs.get('fastRampUpTime', 1)
        slowRampUpTime = kwargs.get('slowRampUpTime', 100)
        fastRampDownTime = kwargs.get('fastRampDownTime', 1)
        slowRampDownTime = kwargs.get('slowRampDownTime', 100)
        onThreshold = kwargs.get('onThreshold', 144)
        offThreshold = kwargs.get('offThreshold', 144)
        floor = kwargs.get('floor', -144)
        minSliceLength = kwargs.get('minSliceLength', 2)
        highPassFreq = kwargs.get('highPassFreq', None)

        cmd.extend([
            '-fastrampup', str(fastRampUpTime),
            '-slowrampup', str(slowRampUpTime),
            '-fastrampdown', str(fastRampDownTime),
            '-slowrampdown', str(slowRampDownTime),
            '-onthreshold', str(onThreshold),
            '-offthreshold', str(offThreshold),
            '-floor', str(floor),
            '-minslicelength', str(minSliceLength)
        ])

        # highpassfreq: High-pass filter cutoff frequency (optional)
        if highPassFreq is not None:
            cmd.extend(['-highpassfreq', str(highPassFreq)])

    elif method == 'onsetslice':
        # Onset slice parameters
        metric = kwargs.get('metric', 0)  # Spectral change metric
        threshold = kwargs.get('threshold', 0.5)
        minSliceLength = kwargs.get('minSliceLength', 2)

        cmd.extend([
            '-metric', str(metric),
            '-threshold', str(threshold),
            '-minslicelength', str(minSliceLength)
        ])

        # filtersize: Filter size for smoothing (optional)
        filtersize = kwargs.get('filtersize', None)
        if filtersize is not None:
            cmd.extend(['-filtersize', str(filtersize)])

        # framedelta: Frame delta parameter (optional)
        framedelta = kwargs.get('framedelta', None)
        if framedelta is not None:
            cmd.extend(['-framedelta', str(framedelta)])

        # fftsettings: expects THREE values [fftsize, hopsize, windowsize]
        fftsettings = kwargs.get('fftsettings', None)
        if fftsettings is not None:
            if isinstance(fftsettings, (list, tuple)) and len(fftsettings) == 3:
                cmd.extend(['-fftsettings', str(fftsettings[0]), str(fftsettings[1]), str(fftsettings[2])])
            else:
                raise ValueError("fftsettings must be a list/tuple of 3 integers [fftsize, hopsize, windowsize]")

    elif method == 'transientslice':
        # Transient slice parameters
        order = kwargs.get('order', 20)
        blocksize = kwargs.get('blocksize', 256)
        padsize = kwargs.get('padsize', None)
        skew = kwargs.get('skew', None)
        threshfwd = kwargs.get('threshfwd', 2)  # Forward threshold
        threshback = kwargs.get('threshback', 1.1)  # Backward threshold
        windowsize = kwargs.get('windowsize', None)
        clumplength = kwargs.get('clumplength', None)
        minSliceLength = kwargs.get('minSliceLength', 2)

        cmd.extend([
            '-order', str(order),
            '-blocksize', str(blocksize),
            '-threshfwd', str(threshfwd),
            '-threshback', str(threshback),
            '-minslicelength', str(minSliceLength)
        ])

        # Optional parameters
        if padsize is not None:
            cmd.extend(['-padsize', str(padsize)])
        if skew is not None:
            cmd.extend(['-skew', str(skew)])
        if windowsize is not None:
            cmd.extend(['-windowsize', str(windowsize)])
        if clumplength is not None:
            cmd.extend(['-clumplength', str(clumplength)])

    else:
        raise ValueError(
            f"Unknown segmentation method '{method}'. "
            "Choose from: noveltyslice, ampslice, onsetslice, transientslice"
        )

    # Run FluCoMa segmentation
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True
        )
    except subprocess.CalledProcessError as e:
        if os.path.exists(indices_path):
            os.unlink(indices_path)
        raise RuntimeError(f"FluCoMa segmentation failed: {e.stderr}")

    # Check if output file was created
    if not os.path.exists(indices_path):
        raise RuntimeError(
            f"FluCoMa did not create output file: {indices_path}\n"
            f"Command: {' '.join(cmd)}\n"
            f"Stdout: {result.stdout}\n"
            f"Stderr: {result.stderr}"
        )

    # Read the indices from output file
    import soundfile as sf

    # Get sample rate of original audio
    audio_info = sf.info(audio_path)
    audio_sr = audio_info.samplerate

    # Read indices (FluCoMa outputs indices as a 1-channel WAV file)
    indices_data, indices_sr = sf.read(indices_path)

    # FluCoMa stores frame indices as sample values in the WAV
    # Each value represents a frame number in the original audio
    frame_indices = indices_data.astype(int)

    # Convert frame indices to timestamps (seconds)
    # Frame index / sample rate = time in seconds
    timestamps = frame_indices / audio_sr

    # Create segmentation file in AudioGuide format
    # AudioGuide expects tab-separated: start_time \t end_time \t metadata
    segmentation_file = audio_path.rsplit('.', 1)[0] + f'_flucoma_{method}.txt'

    # Get audio duration to handle the last segment
    audio_duration = audio_info.duration

    with open(segmentation_file, 'w') as f:
        # AudioGuide format: start \t end \t metadata
        # Convert slice points (onsets) to segments (start-end pairs)
        for i in range(len(timestamps)):
            start_time = timestamps[i]

            # End time is either the next onset or the file end
            if i < len(timestamps) - 1:
                end_time = timestamps[i + 1]
            else:
                end_time = audio_duration

            # Write segment with FluCoMa metadata
            f.write(f"{start_time:.6f}\t{end_time:.6f}\tflucoma_{method}\n")

    # Clean up temp file
    os.unlink(indices_path)

    return segmentation_file


def auto_threshold(audio_path, method='noveltyslice',
                   target_segments_per_second=1.0,
                   tolerance=0.3,
                   **method_kwargs):
    """
    Automatically find optimal threshold for segmentation.

    This function tests multiple threshold values and finds one that produces
    a segment density close to the target (segments per second).

    Args:
        audio_path: Path to audio file
        method: Segmentation method ('noveltyslice', 'onsetslice', etc.)
        target_segments_per_second: Target density (default: 1.0 = one segment per second)
        tolerance: Acceptable deviation from target (default: 0.3 = ±30%)
        **method_kwargs: Method-specific parameters (e.g., algorithm for noveltyslice)

    Returns:
        tuple: (optimal_threshold, segmentation_file_path, segment_count, density)

    Example:
        # Automatically find threshold for ~1 segment per second
        threshold, seg_file, count, density = auto_threshold(
            'audio.wav',
            method='noveltyslice',
            algorithm=0
        )
        print(f"Found threshold={threshold:.2f} giving {count} segments ({density:.2f}/sec)")
    """
    import soundfile as sf

    # Get audio duration
    audio_info = sf.info(audio_path)
    duration = audio_info.duration

    # Define threshold search range based on method
    if method == 'noveltyslice' or method == 'onsetslice':
        thresholds_to_test = [0.2, 0.3, 0.4, 0.5, 0.6, 0.7]
    elif method == 'transientslice':
        thresholds_to_test = [3, 5, 7, 10, 15]
    else:
        # Default range
        thresholds_to_test = [0.2, 0.3, 0.4, 0.5, 0.6, 0.7]

    results = []

    print(f"Auto-detecting optimal threshold for {method}...")
    print(f"Target: {target_segments_per_second:.1f} segments/second (±{tolerance*100:.0f}%)")

    for threshold in thresholds_to_test:
        # Run segmentation with this threshold
        kwargs = method_kwargs.copy()
        kwargs['threshold'] = threshold

        try:
            seg_file = segment_with_flucoma(audio_path, method=method, **kwargs)

            # Count segments
            with open(seg_file, 'r') as f:
                segment_count = len([line for line in f if line.strip()])

            # Calculate density (segments per second)
            density = segment_count / duration

            # Calculate how close to target
            error = abs(density - target_segments_per_second) / target_segments_per_second

            results.append({
                'threshold': threshold,
                'count': segment_count,
                'density': density,
                'error': error,
                'file': seg_file
            })

            print(f"  threshold={threshold:.2f}: {segment_count} segments ({density:.2f}/sec) error={error:.1%}")

        except Exception as e:
            print(f"  threshold={threshold:.2f}: FAILED ({e})")
            continue

    if not results:
        raise RuntimeError("Auto-threshold detection failed: no valid results")

    # Find result closest to target (within tolerance if possible)
    results_within_tolerance = [r for r in results if r['error'] <= tolerance]

    if results_within_tolerance:
        # Use result within tolerance with highest density (more detailed segmentation)
        best = max(results_within_tolerance, key=lambda r: r['density'])
        print(f"\nSelected threshold={best['threshold']:.2f} (within target range)")
    else:
        # No result within tolerance, use closest one
        best = min(results, key=lambda r: r['error'])
        print(f"\nSelected threshold={best['threshold']:.2f} (closest to target, but outside tolerance)")

    print(f"Result: {best['count']} segments ({best['density']:.2f}/sec)")

    return best['threshold'], best['file'], best['count'], best['density']


def noveltyslice(audio_path, algorithm=0, threshold=0.5,
                 kernelsize=None, filtersize=None, minSliceLength=None, fftsettings=None):
    """
    Segment audio using FluCoMa novelty slice (spectral change detection).

    Best for: Melodic material, detecting note changes, timbral shifts

    Args:
        audio_path: Path to audio file
        algorithm: Feature extraction algorithm
            0 = spectrum (default - good for pitch/timbre changes)
            1 = mfcc (good for timbral changes)
            2 = chroma (good for harmonic changes)
        threshold: Detection threshold (0-1, lower = more slices)
                  Use 'auto' to automatically detect optimal threshold
        kernelsize: List/tuple of 2 integers [inner, outer] for kernel size
                   Controls temporal smoothing of novelty curve
                   Example: [3, 5] (default in FluCoMa)
        filtersize: List/tuple of 2 integers [before, after] for smoothing filter
                   Controls smoothing of the novelty curve
                   Example: [1, 3] (default in FluCoMa)
        minSliceLength: Minimum slice length in samples (integer)
                       Prevents very short segments
        fftsettings: List/tuple of 3 integers [fftsize, hopsize, windowsize]
                    FFT analysis parameters (-1 = auto)
                    Example: [1024, -1, -1]

    Returns:
        Path to segmentation file
    """
    if threshold == 'auto':
        _, seg_file, _, _ = auto_threshold(
            audio_path,
            method='noveltyslice',
            algorithm=algorithm,
            kernelsize=kernelsize,
            filtersize=filtersize,
            minSliceLength=minSliceLength,
            fftsettings=fftsettings
        )
        return seg_file

    return segment_with_flucoma(
        audio_path,
        method='noveltyslice',
        algorithm=algorithm,
        threshold=threshold,
        kernelsize=kernelsize,
        filtersize=filtersize,
        minSliceLength=minSliceLength,
        fftsettings=fftsettings
    )


def ampslice(audio_path, fastRampUpTime=1, slowRampUpTime=100,
             fastRampDownTime=1, slowRampDownTime=100,
             onThreshold=144, offThreshold=144, floor=-144, minSliceLength=2):
    """
    Segment audio using FluCoMa amplitude slice (onset detection).

    Best for: Percussive material, clear attacks

    Returns:
        Path to segmentation file
    """
    return segment_with_flucoma(
        audio_path,
        method='ampslice',
        fastRampUpTime=fastRampUpTime,
        slowRampUpTime=slowRampUpTime,
        fastRampDownTime=fastRampDownTime,
        slowRampDownTime=slowRampDownTime,
        onThreshold=onThreshold,
        offThreshold=offThreshold,
        floor=floor,
        minSliceLength=minSliceLength
    )


def onsetslice(audio_path, function=0, threshold=0.5, minSliceLength=2):
    """
    Segment audio using FluCoMa onset slice.

    Best for: Percussive onsets, rhythmic material

    Returns:
        Path to segmentation file
    """
    return segment_with_flucoma(
        audio_path,
        method='onsetslice',
        function=function,
        threshold=threshold,
        minSliceLength=minSliceLength
    )


def transientslice(audio_path, order=20, blocksize=256, threshold=5, minSliceLength=2):
    """
    Segment audio using FluCoMa transient slice.

    Best for: Transient detection, percussive attacks

    Returns:
        Path to segmentation file
    """
    return segment_with_flucoma(
        audio_path,
        method='transientslice',
        order=order,
        blocksize=blocksize,
        threshold=threshold,
        minSliceLength=minSliceLength
    )
