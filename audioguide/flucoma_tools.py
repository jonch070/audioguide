"""
FluCoMa Generic Tool Wrapper

This module provides a generic, future-proof interface to ALL FluCoMa CLI tools.
Instead of hardcoding parameters for each tool, it dynamically discovers available
tools and their parameters, making it compatible with current and future FluCoMa versions.

Available FluCoMa CLI Tools (as of FluCoMa 1.0.7):
- Slicing: ampslice, noveltyslice, onsetslice, transientslice
- Feature Extraction: ampfeature, chroma, loudness, melbands, mfcc, noveltyfeature,
                     onsetfeature, pitch, sinefeature, spectralshape, stats
- Processing: ampgate, audiotransport, hpss, nmf, nmfcross, nmfseed, sines,
             stft, transients

Usage:
    # Generic interface - works with ANY FluCoMa tool
    result = run_flucoma_tool(
        'fluid-pitch',
        source='audio.wav',
        pitch='output_pitch.wav',
        algorithm=2,
        fftsettings=[2048, -1, -1]
    )

    # Or use convenience function
    pitch_data = extract_pitch('audio.wav', algorithm=2)
"""

import os
import subprocess
import shutil
from typing import Dict, List, Optional, Any, Union


def discover_flucoma_tools() -> List[str]:
    """
    Discover all available FluCoMa CLI tools in PATH.

    Returns:
        List of tool names (e.g., ['fluid-pitch', 'fluid-noveltyslice', ...])
    """
    # Try to find one known tool to get the directory
    example_tool = shutil.which('fluid-noveltyslice')
    if not example_tool:
        return []

    tool_dir = os.path.dirname(example_tool)

    # List all fluid-* tools in that directory
    try:
        all_files = os.listdir(tool_dir)
        fluid_tools = [f for f in all_files if f.startswith('fluid-')]
        return sorted(fluid_tools)
    except Exception:
        return []


def run_flucoma_tool(
    tool_name: str,
    **kwargs
) -> subprocess.CompletedProcess:
    """
    Run any FluCoMa CLI tool with arbitrary parameters.

    This is a generic wrapper that works with ANY FluCoMa tool, current or future.
    Parameters are automatically converted to CLI arguments.

    Args:
        tool_name: Name of the FluCoMa tool (e.g., 'fluid-pitch', 'noveltyslice')
        **kwargs: Tool-specific parameters as keyword arguments

    Parameter Handling:
        - Simple values (int, float, str): Converted directly
        - Lists/tuples: Expanded as multiple consecutive arguments
        - None values: Skipped
        - Boolean: Converted to 0/1

    Special Parameters:
        - source: Source audio file (required for most tools)
        - Any output parameters specific to the tool

    Returns:
        CompletedProcess object with stdout, stderr, returncode

    Raises:
        RuntimeError: If tool not found or execution fails

    Examples:
        # Pitch extraction
        run_flucoma_tool('fluid-pitch',
                        source='audio.wav',
                        pitch='pitch.wav',
                        algorithm=2)

        # Novelty slice with all parameters
        run_flucoma_tool('fluid-noveltyslice',
                        source='audio.wav',
                        indices='indices.wav',
                        algorithm=0,
                        threshold=0.4,
                        kernelsize=[3, 5],
                        filtersize=[1, 3])
    """
    # Normalize tool name (allow with or without 'fluid-' prefix)
    if not tool_name.startswith('fluid-'):
        tool_name = f'fluid-{tool_name}'

    # Check if tool exists
    tool_path = shutil.which(tool_name)
    if not tool_path:
        available_tools = discover_flucoma_tools()
        raise RuntimeError(
            f"FluCoMa tool '{tool_name}' not found in PATH.\n"
            f"Available tools: {', '.join(available_tools)}\n"
            "Install from: https://www.flucoma.org/download/"
        )

    # Build command
    cmd = [tool_path]

    # Convert kwargs to CLI arguments
    for key, value in kwargs.items():
        if value is None:
            continue

        # Convert parameter name to CLI format (e.g., source -> -source)
        param_name = f'-{key.lower()}'

        # Handle different value types
        if isinstance(value, bool):
            # Convert boolean to 0/1
            cmd.extend([param_name, '1' if value else '0'])
        elif isinstance(value, (list, tuple)):
            # Expand list/tuple as multiple arguments
            cmd.append(param_name)
            cmd.extend([str(v) for v in value])
        else:
            # Simple value
            cmd.extend([param_name, str(value)])

    # Run tool
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True
        )
        return result
    except subprocess.CalledProcessError as e:
        raise RuntimeError(
            f"FluCoMa tool '{tool_name}' failed:\n"
            f"Command: {' '.join(cmd)}\n"
            f"Error: {e.stderr}"
        )


def get_flucoma_tool_help(tool_name: str) -> str:
    """
    Get help text for a FluCoMa tool.

    Args:
        tool_name: Name of the tool (with or without 'fluid-' prefix)

    Returns:
        Help text from tool's --help output
    """
    if not tool_name.startswith('fluid-'):
        tool_name = f'fluid-{tool_name}'

    tool_path = shutil.which(tool_name)
    if not tool_path:
        return f"Tool '{tool_name}' not found"

    try:
        result = subprocess.run(
            [tool_path, '--help'],
            capture_output=True,
            text=True
        )
        return result.stdout or result.stderr
    except Exception as e:
        return f"Error getting help: {e}"


# Convenience functions for common tools

def extract_pitch(
    audio_path: str,
    output_path: Optional[str] = None,
    algorithm: int = 2,
    **kwargs
) -> str:
    """
    Extract pitch from audio using fluid-pitch.

    Args:
        audio_path: Input audio file
        output_path: Output pitch file (optional, auto-generated if not provided)
        algorithm: Pitch detection algorithm (0=cepstrum, 1=harmonic, 2=yin)
        **kwargs: Additional fluid-pitch parameters

    Returns:
        Path to output pitch file
    """
    import tempfile

    if output_path is None:
        output_path = tempfile.mktemp(suffix='_pitch.wav')

    run_flucoma_tool(
        'fluid-pitch',
        source=audio_path,
        pitch=output_path,
        algorithm=algorithm,
        **kwargs
    )

    return output_path


def extract_loudness(
    audio_path: str,
    output_path: Optional[str] = None,
    **kwargs
) -> str:
    """
    Extract loudness from audio using fluid-loudness.

    Args:
        audio_path: Input audio file
        output_path: Output loudness file (optional)
        **kwargs: Additional fluid-loudness parameters

    Returns:
        Path to output loudness file
    """
    import tempfile

    if output_path is None:
        output_path = tempfile.mktemp(suffix='_loudness.wav')

    run_flucoma_tool(
        'fluid-loudness',
        source=audio_path,
        features=output_path,
        **kwargs
    )

    return output_path


def extract_mfcc(
    audio_path: str,
    output_path: Optional[str] = None,
    numCoeffs: int = 13,
    **kwargs
) -> str:
    """
    Extract MFCC features from audio using fluid-mfcc.

    Args:
        audio_path: Input audio file
        output_path: Output MFCC file (optional)
        numCoeffs: Number of MFCC coefficients (default: 13)
        **kwargs: Additional fluid-mfcc parameters

    Returns:
        Path to output MFCC file
    """
    import tempfile

    if output_path is None:
        output_path = tempfile.mktemp(suffix='_mfcc.wav')

    run_flucoma_tool(
        'fluid-mfcc',
        source=audio_path,
        mfcc=output_path,
        numcoeffs=numCoeffs,
        **kwargs
    )

    return output_path


def extract_spectralshape(
    audio_path: str,
    output_path: Optional[str] = None,
    fftsettings: List[int] = [2048, -1, -1],
    **kwargs
) -> str:
    """
    Extract spectral shape descriptors from audio using fluid-spectralshape.

    Returns 7 values per frame:
    - centroid: Spectral centroid
    - spread: Spectral spread
    - skewness: Spectral skewness
    - kurtosis: Spectral kurtosis
    - rolloff: Spectral rolloff
    - flatness: Spectral flatness
    - crest: Spectral crest

    Args:
        audio_path: Input audio file
        output_path: Output spectral shape file (optional)
        fftsettings: FFT settings [windowSize, hopSize, padSize] default [2048, -1, -1]
        **kwargs: Additional fluid-spectralshape parameters

    Returns:
        Path to output spectral shape file
    """
    import tempfile

    if output_path is None:
        output_path = tempfile.mktemp(suffix='_spectralshape.wav')

    run_flucoma_tool(
        'fluid-spectralshape',
        source=audio_path,
        features=output_path,
        fftsettings=fftsettings,
        **kwargs
    )

    return output_path


# Export public API
__all__ = [
    'discover_flucoma_tools',
    'run_flucoma_tool',
    'get_flucoma_tool_help',
    'extract_pitch',
    'extract_loudness',
    'extract_mfcc',
    'extract_spectralshape',
]
