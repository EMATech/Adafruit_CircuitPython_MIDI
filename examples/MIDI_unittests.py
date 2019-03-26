# The MIT License (MIT)
#
# Copyright (c) 2019 Kevin J. Walters
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import unittest
from unittest.mock import Mock, MagicMock, call

import os
verbose = int(os.getenv('TESTVERBOSE',2))

# adafruit_midi has an import usb_midi
import sys
sys.modules['usb_midi'] = MagicMock()

# Full monty
from adafruit_midi.channel_pressure        import ChannelPressure
from adafruit_midi.control_change          import ControlChange
from adafruit_midi.note_off                import NoteOff
from adafruit_midi.note_on                 import NoteOn
from adafruit_midi.pitch_bend_change       import PitchBendChange
from adafruit_midi.polyphonic_key_pressure import PolyphonicKeyPressure
from adafruit_midi.program_change          import ProgramChange
from adafruit_midi.start                   import Start
from adafruit_midi.stop                    import Stop
from adafruit_midi.system_exclusive        import SystemExclusive
from adafruit_midi.timing_clock            import TimingClock


import adafruit_midi

# Need to test this with a stream of data
# including example below
# small sysex
# too large sysex

### To incorporate into tests
# This is using running status in a rather sporadic manner
# Acutally this now looks more like losing bytes due to being
# overwhelmed by "big" bursts of data
#
# Receiving:  ['0xe0', '0x67', '0x40']
# Receiving:  ['0xe0', '0x72', '0x40']
# Receiving:  ['0x6d', '0x40', '0xe0']
# Receiving:  ['0x5', '0x41', '0xe0']
# Receiving:  ['0x17', '0x41', '0xe0']
# Receiving:  ['0x35', '0x41', '0xe0']
# Receiving:  ['0x40', '0x41', '0xe0']

### TODO - re work these when running status is implemented

class Test_MIDI(unittest.TestCase):
    def test_goodmididatasmall(self):
        self.assertEqual(TODO, TODO)

    def test_goodmididatasmall(self):
        self.assertEqual(TODO, TODO)

    def test_gooddatarunningstatus(self):  ### comment this out as it wont work
        self.assertEqual(TODO, TODO)

    def test_somegoodsomemissingdatabytes(self):
        self.assertEqual(TODO, TODO)

    def test_smallsysex_between_notes(self):
        usb_data = bytearray()
        def write(buffer, length):
            nonlocal usb_data
            usb_data.extend(buffer[0:length])
            
        def read(length):
            nonlocal usb_data
            poppedbytes = usb_data[0:length]
            usb_data = usb_data[len(poppedbytes):]
            return bytes(poppedbytes)
        
        mockedPortIn = Mock()
        mockedPortIn.read = read
        mockedPortOut = Mock()
        mockedPortOut.write = write
        m = adafruit_midi.MIDI(midi_out=mockedPortOut, midi_in=mockedPortIn,
                               out_channel=3, in_channel=3)

        m.send([NoteOn("C4", 0x7f),
                SystemExclusive([0x1f], [1, 2, 3, 4, 5, 6, 7, 8]),
                NoteOff(60, 0x28)])

        (msg1, channel1) = m.read_in_port()
        self.assertIsInstance(msg1, NoteOn)
        self.assertEqual(msg1.note, 60)
        self.assertEqual(msg1.velocity, 0x7f)
        self.assertEqual(channel1, 3)
        
        (msg2, channel2) = m.read_in_port()
        self.assertIsInstance(msg2, SystemExclusive)
        self.assertEqual(msg2.manufacturer_id, bytearray([0x1f]))
        self.assertEqual(msg2.data, bytearray([1, 2, 3, 4, 5, 6, 7, 8]))
        self.assertEqual(channel2, None)  # SysEx does not have a channel
        
        (msg3, channel3) = m.read_in_port()
        self.assertIsInstance(msg3, NoteOff)
        self.assertEqual(msg3.note, 60)
        self.assertEqual(msg3.velocity, 0x28)
        self.assertEqual(channel3, 3)
        
        (msg4, channel4) = m.read_in_port()
        self.assertIsNone(msg4)
        self.assertIsNone(channel4)

    def test_largerthanbuffersysex(self):
        self.assertEqual(TODO, TODO)


class Test_MIDI_send(unittest.TestCase):
    def test_send_basic_single(self):
        #def printit(buffer, len):
        #    print(buffer[0:len])
        mockedPortOut = Mock()
        #mockedPortOut.write = printit
        
        m = adafruit_midi.MIDI(midi_out=mockedPortOut, out_channel=2)

        # Test sending some NoteOn and NoteOff to various channels
        next = 0
        m.send(NoteOn(0x60, 0x7f))
        self.assertEqual(mockedPortOut.write.mock_calls[next],
                         call(b'\x92\x60\x7f', 3))
        next += 1
        m.send(NoteOn(0x64, 0x3f))
        self.assertEqual(mockedPortOut.write.mock_calls[next],
                         call(b'\x92\x64\x3f', 3))
        next += 1
        m.send(NoteOn(0x67, 0x1f))
        self.assertEqual(mockedPortOut.write.mock_calls[next],
                         call(b'\x92\x67\x1f', 3))
        next += 1
        
        m.send(NoteOn(0x60, 0x00))  # Alternative to NoteOff
        self.assertEqual(mockedPortOut.write.mock_calls[next],
                         call(b'\x92\x60\x00', 3))
        next += 1
        m.send(NoteOff(0x64, 0x01))
        self.assertEqual(mockedPortOut.write.mock_calls[next],
                         call(b'\x82\x64\x01', 3))
        next += 1
        m.send(NoteOff(0x67, 0x02))
        self.assertEqual(mockedPortOut.write.mock_calls[next],
                         call(b'\x82\x67\x02', 3))
        next += 1
        
        # Setting channel to non default
        m.send(NoteOn(0x6c, 0x7f), channel=9)
        self.assertEqual(mockedPortOut.write.mock_calls[next],
                         call(b'\x99\x6c\x7f', 3))
        next += 1
        
        m.send(NoteOff(0x6c, 0x7f), channel=9)
        self.assertEqual(mockedPortOut.write.mock_calls[next],
                         call(b'\x89\x6c\x7f', 3))
        next += 1

    def test_send_badnotes(self):
        mockedPortOut = Mock()
        
        m = adafruit_midi.MIDI(midi_out=mockedPortOut, out_channel=2)

        # Test sending some NoteOn and NoteOff to various channels
        next = 0
        m.send(NoteOn(60, 0x7f))
        self.assertEqual(mockedPortOut.write.mock_calls[next],
                         call(b'\x92\x3c\x7f', 3))
        next += 1
        with self.assertRaises(ValueError):
            m.send(NoteOn(64, 0x80)) # Velocity > 127 - illegal value

        with self.assertRaises(ValueError):
            m.send(NoteOn(67, -1))

        # test after exceptions to ensure sending is still ok
        m.send(NoteOn(72, 0x7f))
        self.assertEqual(mockedPortOut.write.mock_calls[next],
                         call(b'\x92\x48\x7f', 3))
        next += 1
        
    def test_send_basic_sequences(self):
        #def printit(buffer, len):
        #    print(buffer[0:len])
        mockedPortOut = Mock()
        #mockedPortOut.write = printit
        
        m = adafruit_midi.MIDI(midi_out=mockedPortOut, out_channel=2)

        # Test sending some NoteOn and NoteOff to various channels
        next = 0
        # Test sequences with list syntax and pass a tuple too
        note_list = [NoteOn(0x6c, 0x51),
                     NoteOn(0x70, 0x52),
                     NoteOn(0x73, 0x53)];
        note_tuple = tuple(note_list)
        m.send(note_list, channel=10)
        self.assertEqual(mockedPortOut.write.mock_calls[next],
                         call(b'\x9a\x6c\x51\x9a\x70\x52\x9a\x73\x53', 9),
                         "The implementation writes in one go, single 9 byte write expected")
        next += 1
        m.send(note_tuple, channel=11)
        self.assertEqual(mockedPortOut.write.mock_calls[next],
                         call(b'\x9b\x6c\x51\x9b\x70\x52\x9b\x73\x53', 9),
                         "The implementation writes in one go, single 9 byte write expected")
        next += 1

class Test_MIDI_send_receive_loop(unittest.TestCase):
    def test_do_something_that_collects_sent_data_then_parses_it(self):
        self.assertEqual(TODO, TODO)

        
if __name__ == '__main__':
    unittest.main(verbosity=verbose)
