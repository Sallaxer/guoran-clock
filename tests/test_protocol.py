import sys, unittest
from datetime import datetime
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from protocol import SWITCHES, StateBuffer, rgb_command, system_time, time_command, parse_state
class ProtocolTests(unittest.TestCase):
    def setUp(self):
        self.frame='R255-G100-B000'+''.join('S'+key+str(i%2) for i,(key,_) in enumerate(SWITCHES))+'A07:30AA19:45BT06:00OT23:00CCSS'
    def test_frame(self):
        self.assertEqual(len(self.frame),93)
        state=parse_state(self.frame)
        self.assertEqual(state['rgb'],(255,100,0))
        self.assertEqual(state['times'],{'alarm1':'07:30','alarm2':'19:45','on':'06:00','off':'23:00'})
        self.assertEqual(state['switches']['A'],False)
        self.assertTrue(state['switches']['F'])
    def test_every_split_boundary(self):
        for i in range(1,93):
            buf=StateBuffer()
            self.assertEqual(buf.feed(self.frame[:i].encode()),[])
            self.assertEqual(buf.feed(self.frame[i:].encode()),[parse_state(self.frame)])
    def test_noise_and_multiple_frames(self):
        buf=StateBuffer()
        result=[]
        for byte in ('noiseRbad'+self.frame+self.frame).encode():
            result.extend(buf.feed(bytes([byte])))
        self.assertEqual(result,[parse_state(self.frame)]*2)
    def test_commands(self):
        self.assertEqual(rgb_command((0,255,7)),'R000-G255-B007')
        self.assertEqual(time_command('off','23:59'),'T23:59C')
        self.assertEqual(system_time(datetime(2026,10,4,9,5,3)),'$2026-10-04;09:05:03;00')
        self.assertEqual(system_time(datetime(2026,10,3,9,5,3)),'$2026-10-03;09:05:03;06')
        for value in ['24:00','7:30','12:60','bad']:
            with self.assertRaises(ValueError): time_command('on',value)
    def test_real_firmware_unknown_fields_do_not_hide_state(self):
        actual='R088-G082-B023S10S20S30S40S50S60S70S80S90S01SA1SB0SCKSD0SE1SF1A00:00AA00:00BT08:00OT44:29CCSS'
        state=parse_state(actual)
        self.assertIsNone(state['switches']['C'])
        self.assertEqual(state['raw_switches']['C'],'K')
        self.assertEqual(state['times']['on'],'08:00')
        self.assertIsNone(state['times']['off'])
        self.assertEqual(state['raw_times']['off'],'44:29')
        self.assertEqual(state['rgb'],(88,82,23))
        self.assertTrue(state['switches']['A'])
        for split in range(1,93):
            buf=StateBuffer()
            self.assertEqual(buf.feed(actual[:split].encode()),[])
            self.assertEqual(buf.feed(actual[split:].encode()),[state])
if __name__=='__main__': unittest.main()
