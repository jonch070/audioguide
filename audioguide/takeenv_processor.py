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


def add_static_takeenv(tracks, static_gain_db=0.0, attack=0.0, sustain=1.0, release=0.0):
    """
    Add TAKEENV to all items in tracks with optional ASR envelope.

    Args:
        tracks: List of (trackname, items, origin) tuples
        static_gain_db: Static gain offset in dB (default 0.0)
        attack: Attack time in seconds (default 0.0 - instant)
        sustain: Sustain level as ratio 0-1 (default 1.0 - full gain)
        release: Release time in seconds (default 0.0 - instant)

    Returns:
        Modified tracks list with gain_envelope added to items
    """
    # Convert sustain ratio to dB (ratio 1.0 = 0dB, ratio 0.0 = -inf dB)
    if sustain <= 0:
        sustain_db = -60.0  # Effectively silent
    else:
        sustain_db = 20.0 * np.log10(sustain)
    
    enhanced_tracks = []

    for trackname, items, origin in tracks:
        enhanced_items = []

        for item in items:
            # Copy item dict
            enhanced_item = dict(item)

            # Calculate envelope points based on ASR
            duration = item['orig_duration']
            start_time = item['time']
            end_time = start_time + duration

            # ASR envelope:
            # Point 1: start_time, -inf dB (silence at attack start)
            # Point 2: start_time + attack, sustain_db (attack reaches sustain level)
            # Point 3: end_time - release, sustain_db (release starts)
            # Point 4: end_time, -inf dB (release ends at silence)
            
            attack_time = start_time + attack
            release_start = end_time - release
            
            # Clamp to valid range
            if attack > duration:
                attack_time = end_time
            if release > duration:
                release_start = start_time
            
            # Build envelope points
            envelope = []
            
            # Start point (silence)
            envelope.append((start_time, -60.0))
            
            # Attack end point (reach sustain level)
            if attack > 0:
                envelope.append((attack_time, sustain_db))
            else:
                # Instant attack - just go to sustain
                envelope.append((start_time, sustain_db))
            
            # Release start point (begin release)
            if release > 0 and release_start > attack_time:
                envelope.append((release_start, sustain_db))
            
            # End point (silence)
            envelope.append((end_time, -60.0))
            
            # Apply static gain offset to all points
            final_envelope = [(t, g + static_gain_db) for t, g in envelope]
            
            enhanced_item['gain_envelope'] = final_envelope

            enhanced_items.append(enhanced_item)

        enhanced_tracks.append((trackname, enhanced_items, origin))

    return enhanced_tracks


def add_dynamic_takeenv(tracks, target_segments=None, attack=0.0, sustain=1.0, release=0.0):
    """
    Add time-varying TAKEENV based on amplitude analysis.

    Args:
        tracks: List of (trackname, items, origin) tuples
        target_segments: Optional list of target segments for envelope extraction
        attack: Attack time in seconds (default 0.0 - instant)
        sustain: Sustain level as ratio 0-1 (default 1.0 - full gain)
        release: Release time in seconds (default 0.0 - instant)

    Returns:
        Modified tracks list with gain_envelope added to items

    Note: This is a placeholder for future dynamic envelope generation
    """
    # For now, just add static envelopes with ASR
    # Future: Analyze target amplitude and create matching envelopes
    return add_static_takeenv(tracks, static_gain_db=-3.0, attack=attack, sustain=sustain, release=release)


def process_tracks_for_takeenv(tracks, enable_takeenv=False, static_gain_db=0.0, dynamic=False, attack=0.0, sustain=1.0, release=0.0):
    """
    Main entry point: Process tracks to add TAKEENV automation.

    Args:
        tracks: AudioGuide track data
        enable_takeenv: Enable TAKEENV processing
        static_gain_db: Static gain offset (used if not dynamic)
        dynamic: Use dynamic envelope generation
        attack: Attack time in seconds (default 0.0 - instant)
        sustain: Sustain level as ratio 0-1 (default 1.0 - full gain)
        release: Release time in seconds (default 0.0 - instant)

    Returns:
        Processed tracks (or original if TAKEENV disabled)
    """
    if not enable_takeenv:
        return tracks

    if dynamic:
        return add_dynamic_takeenv(tracks, attack=attack, sustain=sustain, release=release)
    else:
        return add_static_takeenv(tracks, static_gain_db, attack=attack, sustain=sustain, release=release)
