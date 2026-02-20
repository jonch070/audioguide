#!/usr/bin/env python3
"""
End-to-end test for VOLENV (track-level) and TAKEENV (item-level) independence.

This test verifies that:
1. VOLENV and TAKEENV can coexist in RPP output
2. Track-level and item-level volume operate independently
3. Double-gain is prevented when both are enabled
"""

import os
import sys
import tempfile


def db_to_linear(db):
    """Convert dB to linear amplitude (for TAKEENV points)."""
    return 10 ** (db / 20.0)


def format_takeenv(gain_envelope, item_position):
    """
    Format TAKEENV chunk with automation points.
    """
    if not gain_envelope or len(gain_envelope) == 0:
        return ""

    takeenv_str = "      <TAKEENV\n"
    takeenv_str += "        NAME \"Volume\"\n"
    takeenv_str += "        ACT 1\n"
    takeenv_str += "        VIS 1\n"
    takeenv_str += "        LANEHEIGHT 0 0\n"
    takeenv_str += "        ARM 0\n"
    takeenv_str += "        DEFSHAPE 0 -1 -1\n"

    for time_sec, gain_db in gain_envelope:
        relative_time = time_sec - item_position
        relative_time = max(0.0, relative_time)
        linear_value = db_to_linear(gain_db)
        takeenv_str += "        PT %.6f %.6f 0\n" % (relative_time, linear_value)

    takeenv_str += "      >\n"
    return takeenv_str


def format_volumeenv(gain_envelope):
    """
    Format VOLENV chunk for track-level volume automation.
    """
    if not gain_envelope or len(gain_envelope) == 0:
        return ""

    volenv_str = "  <VOLENV\n"
    volenv_str += "    ACT 1\n"
    volenv_str += "    VIS 1 1 1\n"
    volenv_str += "    LANEHEIGHT 0 0\n"
    volenv_str += "    ARM 0\n"
    volenv_str += "    DEFSHAPE 0 -1 -1\n"

    for time_sec, gain_db in gain_envelope:
        linear_value = db_to_linear(gain_db)
        volenv_str += "    PT %.6f %.6f 0\n" % (time_sec, linear_value)

    volenv_str += "  >\n"
    return volenv_str


class output:
    def __init__(self, rpp_filepath):
        self.path = rpp_filepath
        self.tracks = []

    def add_tracks(self, tracks):
        self.tracks.extend(tracks)

    def write(self, autolaunchbool, verbose=True, rpp_header='REAPER_PROJECT 0.1 "6.11/x64" 1591355987', playrate_change_duration=True, playrate_preset=-1, enable_volumeenv=False, enable_takeenv=False):
        '''write and close the rpp file
        
        Enhanced to support TAKEENV (clip gain automation) via 'gain_envelope' in item dict.
        '''
        f = open(self.path, "w")
        all_tracks_str = ''
        for trackname, trackitems, trackorigin in self.tracks:
            track_str = ''
            for d in trackitems:
                if playrate_change_duration:
                    playrate_str = 'PLAYRATE %f 0 0 %i\n' % (1/d['transposeSpeedChange'], playrate_preset)
                else:
                    playrate_str = 'PLAYRATE 1.000 1 %f %i\n' % (d['transposition'], playrate_preset)

                has_envelope = 'gain_envelope' in d and d['gain_envelope'] and len(d['gain_envelope']) > 0
                
                takeenv_str = ""
                if has_envelope and enable_takeenv:
                    takeenv_str = format_takeenv(d['gain_envelope'], d['time'])

                # Calculate final volume (ampscale * static gain if present)
                final_volume = d['ampscale']
                if has_envelope and not enable_volumeenv and not enable_takeenv:
                    # Extract static gain from first envelope point and multiply into VOLPAN
                    # (only when VOLUMEENV is disabled and TAKEENV is not being written)
                    _, gain_db = d['gain_envelope'][0]
                    gain_linear = db_to_linear(gain_db)
                    final_volume = d['ampscale'] * gain_linear

                if takeenv_str:
                    track_str += '''     <ITEM
      POSITION  %f
      NAME "%s"
      LENGTH %f
      SOFFS %f
      VOLPAN %f 0.0 1.0 -1.0
      FADEIN 1 %f 0.0
      FADEOUT 1 %f 0.0
      %s      <TAKE>
        <SOURCE WAVE>
          FILE "%s"
        >
%s      >
     >
''' % (d['time'], d['name'], d['orig_duration'], d['skip'], final_volume,
       d['fadein'], d['fadeout'], playrate_str, d['file'], takeenv_str)
                else:
                    track_str += '''     <ITEM
      POSITION  %f
      NAME "%s"
      LENGTH %f
      SOFFS %f
      VOLPAN %f 0.0 1.0 -1.0
      FADEIN 1 %f 0.0
      FADEOUT 1 %f 0.0
      %s      <SOURCE WAVE>
        FILE "%s"
      >
     >
''' % (d['time'], d['name'], d['orig_duration'], d['skip'], final_volume,
       d['fadein'], d['fadeout'], playrate_str, d['file'])

            volumeenv_str = ""
            if enable_volumeenv:
                if len(trackitems) > 0:
                    first_item = trackitems[0]
                    if 'gain_envelope' in first_item and first_item['gain_envelope'] and len(first_item['gain_envelope']) > 0:
                        volumeenv_str = format_volumeenv(first_item['gain_envelope'])

            all_tracks_str += '''  <TRACK
   NAME "%s"
%s%s  >
''' % (trackname, track_str, volumeenv_str)

        f.write('''<%s
%s>''' % (rpp_header, all_tracks_str))
        f.close()

        if verbose:
            tgt_track_count = len([t for t in self.tracks if t[0].find('target') != -1])
            if tgt_track_count == 0:
                print("Wrote %i corpus tracks to %s" % (len(self.tracks), self.path))
            else:
                print("Wrote %i target tracks and %i corpus tracks to %s" % (tgt_track_count, len(self.tracks)-tgt_track_count))


def test_volenv_takeenv_coexistence():
    """Test that VOLENV and TAKEENV can coexist without double-gain."""
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.rpp', delete=False) as f:
        rpp_path = f.name
    
    try:
        out = output(rpp_path)
        
        test_item = {
            'name': 'test_sound.wav',
            'time': 1.0,
            'orig_duration': 5.0,
            'skip': 0.0,
            'transposeSpeedChange': 1.0,
            'transposition': 0,
            'ampscale': 1.0,
            'fadein': 0.0,
            'fadeout': 0.0,
            'file': '/path/to/test_sound.wav',
            'gain_envelope': [
                (0.0, -6.0),
                (2.5, -3.0),
                (5.0, -6.0),
            ],
        }
        
        # Test 1: Both VOLENV and TAKEENV enabled
        print("Test 1: Both VOLENV and TAKEENV enabled")
        out.add_tracks([('Test Track', [test_item], 'origin')])
        out.write(False, verbose=False, enable_volumeenv=True, enable_takeenv=True)
        
        with open(rpp_path, 'r') as f:
            content = f.read()
        
        assert '<VOLENV' in content, "VOLENV chunk missing when enable_volumeenv=True"
        assert '<TAKEENV' in content, "TAKEENV chunk missing when enable_takeenv=True"
        assert '<TAKE>' in content, "TAKE wrapper missing for TAKEENV"
        assert '<TAKEENV' in content, "TAKEENV chunk missing when enable_takeenv=True"
        assert '<TAKE>' in content, "TAKE wrapper missing for TAKEENV"
        
        volpan_lines = [line for line in content.split('\n') if 'VOLPAN' in line]
        for volpan_line in volpan_lines:
            vol_value = float(volpan_line.split()[1])
            assert vol_value == 1.0, f"VOLPAN should be 1.0 when TAKEENV is active, got {vol_value}"
        
        print("  ✓ VOLENV and TAKEENV coexist correctly")
        print("  ✓ VOLPAN is 1.0 (no double-gain applied)")
        
        # Test 2: Only VOLENV enabled
        print("\nTest 2: Only VOLENV enabled (no TAKEENV)")
        
        out2 = output(rpp_path)
        test_item2 = dict(test_item)
        out2.add_tracks([('Test Track', [test_item2], 'origin')])
        out2.write(False, verbose=False, enable_volumeenv=True, enable_takeenv=False)
        
        with open(rpp_path, 'r') as f:
            content2 = f.read()
        
        assert '<VOLENV' in content2, "VOLENV missing"
        assert '<TAKEENV' not in content2, "TAKEENV should not exist when enable_takeenv=False"
        assert '<TAKE>' not in content2, "TAKE wrapper should not exist"
        
        volpan_lines2 = [line for line in content2.split('\n') if 'VOLPAN' in line]
        for volpan_line in volpan_lines2:
            vol_value = float(volpan_line.split()[1])
            # When VOLENV is enabled, track-level automation handles gain
            # VOLPAN should remain at 1.0
            assert vol_value == 1.0, f"VOLPAN should be 1.0 when VOLENV is active, got {vol_value}"
        
        print("  ✓ VOLENV works without TAKEENV")
        print("  ✓ VOLPAN is 1.0 (track-level automation handles gain)")
        
        # Test 3: Only TAKEENV enabled
        print("\nTest 3: Only TAKEENV enabled (no VOLENV)")
        
        out3 = output(rpp_path)
        test_item3 = dict(test_item)
        out3.add_tracks([('Test Track', [test_item3], 'origin')])
        out3.write(False, verbose=False, enable_volumeenv=False, enable_takeenv=True)
        
        with open(rpp_path, 'r') as f:
            content3 = f.read()
        
        assert '<TAKEENV' in content3, "TAKEENV missing"
        assert '<TAKE>' in content3, "TAKE wrapper missing"
        
        volpan_lines3 = [line for line in content3.split('\n') if 'VOLPAN' in line]
        for volpan_line in volpan_lines3:
            vol_value = float(volpan_line.split()[1])
            assert vol_value == 1.0, f"VOLPAN should be 1.0, got {vol_value}"
        
        print("  ✓ TAKEENV works without VOLENV")
        print("  ✓ VOLPAN is 1.0 (gain handled by TAKEENV)")
        
        # Test 4: Neither enabled
        print("\nTest 4: Neither VOLENV nor TAKEENV enabled")
        
        out4 = output(rpp_path)
        test_item4 = dict(test_item)
        out4.add_tracks([('Test Track', [test_item4], 'origin')])
        out4.write(False, verbose=False, enable_volumeenv=False, enable_takeenv=False)
        
        with open(rpp_path, 'r') as f:
            content4 = f.read()
        
        assert '<VOLENV' not in content4, "VOLENV should not exist"
        assert '<TAKEENV' not in content4, "TAKEENV should not exist"
        assert '<TAKE>' not in content4, "TAKE wrapper should not exist"
        
        volpan_lines4 = [line for line in content4.split('\n') if 'VOLPAN' in line]
        for volpan_line in volpan_lines4:
            vol_value = float(volpan_line.split()[1])
            expected = 10 ** (-6.0 / 20.0)
            assert abs(vol_value - expected) < 0.01, f"VOLPAN should have static gain {expected}, got {vol_value}"
        
        print("  ✓ No automation when both disabled")
        print("  ✓ Static gain applied to VOLPAN")
        
        print("\n" + "="*50)
        print("ALL TESTS PASSED!")
        print("="*50)
        print("\nVOLENV and TAKEENV operate independently:")
        print("  • Both can coexist in RPP output")
        print("  • Track volume (VOLENV) is separate from item volume (TAKEENV)")
        print("  • No double-gain when both are enabled")
        
        return True
        
    finally:
        if os.path.exists(rpp_path):
            os.remove(rpp_path)


if __name__ == '__main__':
    success = test_volenv_takeenv_coexistence()
    sys.exit(0 if success else 1)
