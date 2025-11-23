############################################################################
## This software is distributed for free, without warranties of any kind. ##
## TAKEENV post-processor for AudioGuide RPP output                        ##
############################################################################

"""
Post-processes AudioGuide track data to add TAKEENV gain automation.

This module adds gain_envelope to item dictionaries after standard
AudioGuide processing, enabling clip gain automation in Reaper RPP output.
"""

import numpy as np


def add_static_takeenv(tracks, static_gain_db=0.0):
    """
    Add simple static TAKEENV to all items in tracks.

    Args:
        tracks: List of (trackname, items, origin) tuples
        static_gain_db: Static gain offset in dB (default 0.0)

    Returns:
        Modified tracks list with gain_envelope added to items
    """
    enhanced_tracks = []

    for trackname, items, origin in tracks:
        enhanced_items = []

        for item in items:
            # Copy item dict
            enhanced_item = dict(item)

            # Add simple two-point envelope (start and end)
            duration = item['orig_duration']
            start_time = item['time']
            end_time = start_time + duration

            # Static gain: same value at start and end
            enhanced_item['gain_envelope'] = [
                (start_time, static_gain_db),
                (end_time, static_gain_db)
            ]

            enhanced_items.append(enhanced_item)

        enhanced_tracks.append((trackname, enhanced_items, origin))

    return enhanced_tracks


def add_dynamic_takeenv(tracks, target_segments=None):
    """
    Add time-varying TAKEENV based on amplitude analysis.

    Args:
        tracks: List of (trackname, items, origin) tuples
        target_segments: Optional list of target segments for envelope extraction

    Returns:
        Modified tracks list with gain_envelope added to items

    Note: This is a placeholder for future dynamic envelope generation
    """
    # For now, just add static envelopes
    # Future: Analyze target amplitude and create matching envelopes
    return add_static_takeenv(tracks, static_gain_db=-3.0)


def process_tracks_for_takeenv(tracks, enable_takeenv=False, static_gain_db=0.0, dynamic=False):
    """
    Main entry point: Process tracks to add TAKEENV automation.

    Args:
        tracks: AudioGuide track data
        enable_takeenv: Enable TAKEENV processing
        static_gain_db: Static gain offset (used if not dynamic)
        dynamic: Use dynamic envelope generation

    Returns:
        Processed tracks (or original if TAKEENV disabled)
    """
    if not enable_takeenv:
        return tracks

    if dynamic:
        return add_dynamic_takeenv(tracks)
    else:
        return add_static_takeenv(tracks, static_gain_db)
