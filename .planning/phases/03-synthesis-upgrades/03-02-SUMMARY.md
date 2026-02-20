---
phase: 03-synthesis-upgrades
plan: 02
status: complete
---

## Plan 03-02 Summary: MIDI Output & Stochastic Selection

### Completed Tasks

1. **Added MIDI Config Options** (`audioguide/defaults.py`)
   - MIDI_FILEPATH: Output path for MIDI file
   - MIDI_CHANNEL: Channel 1-16 (default 1)
   - MIDI_VELOCITY_SOURCE: 'target_loudness', 'corpus_velocity', 'fixed'
   - MIDI_VELOCITY_FIXED: Fixed velocity when source='fixed'
   - MIDI_TRANSPOSE_OCTAVES: Transpose in octaves
   - MIDI_INSTRUMENT: GM instrument name

2. **Added Stochastic Selection Options** (`audioguide/defaults.py`)
   - STOCHASTIC_SELECTION: Enable probabilistic selection
   - STOCHASTIC_TEMPERATURE: Softmax temperature
   - STOCHASTIC_TOP_K: Consider top K matches
   - STOCHASTIC_DIVERSITY_PENALTY: Penalize repeated files

3. **Created MIDI Module** (`audioguide/fileoutput/midi.py`)
   - MIDIEvent dataclass with pitch, velocity, timing
   - write_midi_file() - Standard MIDI File format
   - create_midi_from_output_events() - Convert AudioGuide events
   - freq_to_midi(), velocity_from_loudness() helpers

4. **Added Stochastic Selection** (`audioguide/spectrallayering.py`)
   - softmax() - Temperature-scaled probability distribution
   - stochastic_candidates() - Probabilistic selection
   - diversity_penalty_score() - Track corpus diversity

### Verification Results

```
✓ 440 Hz = MIDI note 69
✓ -12 dB = velocity 102
✓ Stochastic selection works with temperature
```

### Files Created/Modified

- Created: `audioguide/fileoutput/midi.py`
- Modified: `audioguide/defaults.py`
- Modified: `audioguide/spectrallayering.py`
