"""
AudioGuide MIDI Output Module

Provides MIDI file output for integration with DAWs and virtual instruments.
"""

import struct
from typing import List, Optional
from dataclasses import dataclass


@dataclass
class MIDIEvent:
    """Represents a single MIDI note event."""
    pitch: int  # MIDI note number (0-127)
    velocity: int  # Velocity (0-127)
    start_time_sec: float  # Start time in seconds
    duration_sec: float  # Note duration in seconds
    channel: int = 1  # MIDI channel (1-16)
    
    def __post_init__(self):
        self.pitch = max(0, min(127, self.pitch))
        self.velocity = max(0, min(127, self.velocity))
        self.channel = max(1, min(16, self.channel))


def freq_to_midi(freq: float) -> int:
    """Convert frequency (Hz) to MIDI note number."""
    if freq <= 0:
        return 60  # Default to middle C
    return int(round(69 + 12 * np.log2(freq / 440.0)))


def midi_to_freq(midi: int) -> float:
    """Convert MIDI note number to frequency (Hz)."""
    return 440.0 * 2 ** ((midi - 69) / 12.0)


def velocity_from_loudness(db: float) -> int:
    """Convert loudness in dB to MIDI velocity (0-127)."""
    # Map -60dB to 0, 0dB to 127
    velocity = int(round((db + 60) * 127 / 60))
    return max(1, min(127, velocity))


def db_to_velocity(db: float) -> int:
    """Alias for velocity_from_loudness for clarity."""
    return velocity_from_loudness(db)


# MIDI file format constants
MIDI_HEADER = b'MThd'
MIDI_TRACK = b'MTrk'


def write_midi_file(events: List[MIDIEvent], filepath: str,
                    ticks_per_beat: int = 480,
                    tempo: float = 500000) -> None:
    """
    Write MIDI events to a Standard MIDI File.
    
    Args:
        events: List of MIDIEvent objects
        filepath: Output .mid file path
        ticks_per_beat: Resolution (default 480 ticks per beat)
        tempo: Microseconds per beat (default 500000 = 120 BPM)
    """
    if not events:
        # Write empty track
        events = []
    
    # Sort events by start time
    events = sorted(events, key=lambda e: e.start_time_sec)
    
    # Convert to tick times
    ticks_per_sec = 1000000 / tempo * ticks_per_beat
    
    # Build track data
    track_data = b''
    
    # Set tempo (microseconds per beat)
    track_data += write_var_length(int(tempo / 4))  # Delta time
    track_data += struct.pack('>BBBB', 0xFF, 0x51, 0x03, int(tempo / 65536))
    track_data += struct.pack('>BBBB', int(tempo / 256) % 256, tempo % 256)
    
    last_tick = 0
    
    for event in events:
        # Note ON
        tick = int(event.start_time_sec * ticks_per_sec)
        delta = tick - last_tick
        last_tick = tick
        
        # Note ON (status byte = 0x90 + channel-1)
        status_on = 0x90 | (event.channel - 1)
        track_data += write_var_length(delta)
        track_data += struct.pack('>BBB', status_on, event.pitch, event.velocity)
        
        # Note OFF
        off_tick = int((event.start_time_sec + event.duration_sec) * ticks_per_sec)
        delta_off = off_tick - last_tick
        last_tick = off_tick
        
        # Note OFF (status byte = 0x80 + channel-1)
        status_off = 0x80 | (event.channel - 1)
        track_data += write_var_length(delta_off)
        track_data += struct.pack('>BBB', status_off, event.pitch, 0)
    
    # End of track
    track_data += write_var_length(0)
    track_data += struct.pack('>BB', 0xFF, 0x2F)
    
    # Write file
    with open(filepath, 'wb') as f:
        # Header chunk
        f.write(MIDI_HEADER)
        f.write(struct.pack('>IHHI', 6, 1, 1, ticks_per_beat))  # Format 1, 1 track
        
        # Track chunk
        f.write(MIDI_TRACK)
        f.write(struct.pack('>I', len(track_data)))
        f.write(track_data)


def write_var_length(value: int) -> bytes:
    """Write a variable-length quantity."""
    result = []
    result.append(value & 0x7F)
    value >>= 7
    while value > 0:
        result.append((value & 0x7F) | 0x80)
        value >>= 7
    result.reverse()
    return bytes(result)


def create_midi_from_output_events(output_events, 
                                   midi_channel: int = 1,
                                   velocity_source: str = 'target_loudness',
                                   velocity_fixed: int = 100,
                                   transpose_octaves: int = 0) -> List[MIDIEvent]:
    """
    Convert AudioGuide output events to MIDI events.
    
    Args:
        output_events: List of AudioGuide output event objects
        midi_channel: MIDI channel (1-16)
        velocity_source: 'target_loudness', 'corpus_velocity', or 'fixed'
        velocity_fixed: Fixed velocity when source is 'fixed'
        transpose_octaves: Octaves to transpose
        
    Returns:
        List of MIDIEvent objects
    """
    import numpy as np
    
    midi_events = []
    
    for event in output_events:
        try:
            # Get pitch from corpus segment
            if hasattr(event, 'sfseghandle') and hasattr(event.sfseghandle, 'MIDIPitch'):
                midi_note = int(event.sfseghandle.MIDIPitch)
            elif hasattr(event, 'transposition'):
                # Use transposition to calculate pitch
                midi_note = 60 + int(event.transposition * 12)
            else:
                # Default to middle C
                midi_note = 60
            
            # Apply transpose
            midi_note += transpose_octaves * 12
            midi_note = max(0, min(127, midi_note))
            
            # Get velocity
            if velocity_source == 'fixed':
                velocity = velocity_fixed
            elif velocity_source == 'corpus_velocity':
                # Use corpus segment's velocity if available
                if hasattr(event, 'sfseghandle') and hasattr(event.sfseghandle, 'loudness'):
                    db = event.sfseghandle.loudness
                    velocity = velocity_from_loudness(db)
                else:
                    velocity = velocity_fixed
            else:  # 'target_loudness'
                # Estimate from event gain
                if hasattr(event, 'gain'):
                    gain_db = 20 * np.log10(max(event.gain, 0.0001))
                    velocity = velocity_from_loudness(gain_db)
                else:
                    velocity = velocity_fixed
            
            # Get timing
            start_time = event.timeInScore if hasattr(event, 'timeInScore') else 0
            duration = event.durationSec if hasattr(event, 'durationSec') else 1.0
            
            midi_event = MIDIEvent(
                pitch=midi_note,
                velocity=velocity,
                start_time_sec=start_time,
                duration_sec=max(0.01, duration),
                channel=midi_channel
            )
            midi_events.append(midi_event)
            
        except Exception as e:
            # Skip events that can't be converted
            continue
    
    return midi_events


# Import numpy for the conversion function
import numpy as np
