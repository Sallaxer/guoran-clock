import asyncio
import json
import sys
import tempfile
import time
import unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import guoran_desktop as desktop

class ScheduleTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.patcher=patch.object(desktop,'PREFERENCES',Path(self.temp.name)/'prefs.json')
        self.patcher.start()
        self.api=desktop.Api()
        self.sent=[]
        async def send(command): self.sent.append(command)
        self.api._bt.send=send
    def tearDown(self):
        self.api._shutdown();self.patcher.stop();self.temp.cleanup()
    def done(self):
        deadline=time.monotonic()+2
        while time.monotonic()<deadline:
            state=self.api.poll()
            if not state['busy']:return state
            time.sleep(.01)
        self.fail('Operation timed out')
    def test_enable_sends_both_times_before_flag(self):
        self.assertTrue(self.api.apply_schedule('08:00','00:15',True)['ok'])
        state=self.done()
        self.assertEqual(self.sent,['T08:00O','T00:15C','S01'])
        self.assertEqual(state['requested']['times:off'],'00:15')
        self.assertTrue(state['requested']['switches:0'])
    def test_invalid_second_time_sends_nothing(self):
        self.assertFalse(self.api.apply_schedule('08:00','44:29',True)['ok'])
        self.assertEqual(self.sent,[])
    def test_disable_does_not_rewrite_times(self):
        self.api.apply_schedule('','',False);self.done()
        self.assertEqual(self.sent,['S00'])
    def test_failure_does_not_enable_schedule(self):
        async def send(command):
            self.sent.append(command)
            if command.endswith('C'):raise RuntimeError('Link lost')
        self.api._bt.send=send
        self.api.apply_schedule('08:00','00:15',True)
        state=self.done()
        self.assertEqual(self.sent,['T08:00O','T00:15C'])
        self.assertEqual(state['error'],'Link lost')
        self.assertNotIn('switches:0',state['requested'])
    def test_draft_is_local_and_survives_theme_language_changes(self):
        self.api.save_schedule('08:00','00:15')
        self.api.set_language('en');self.api.set_theme('dark')
        self.assertEqual(self.sent,[])
        another=desktop.Api()
        try:
            state=another.poll()
            self.assertEqual(state['schedule'],{'on':'08:00','off':'00:15'})
            self.assertEqual(state['language'],'en')
            self.assertEqual(state['theme'],'dark')
            self.assertEqual(state['status'],'Connect your clock to begin')
        finally:another._shutdown()
    def test_operation_lock_prevents_interleaving(self):
        self.api._operation_lock.acquire()
        try:self.assertFalse(self.api.apply_schedule('08:00','00:15',True)['ok'])
        finally:self.api._operation_lock.release()
        self.assertEqual(self.sent,[])

    def test_set_prepares_with_back_without_toggling_power(self):
        self.assertTrue(self.api.remote_key('K07')['ok'])
        self.done()
        self.assertEqual(self.sent, ['K05', 'K07'])

    def test_failed_back_does_not_send_set(self):
        async def send(command):
            self.sent.append(command)
            raise RuntimeError('Link lost')
        self.api._bt.send = send
        self.api.remote_key('K07')
        self.assertEqual(self.done()['error'], 'Link lost')
        self.assertEqual(self.sent, ['K05'])

    def test_other_remote_keys_stay_single_commands(self):
        for key in ('K04', 'K05', 'K06', 'K08', 'K09'):
            self.api.remote_key(key)
            self.done()
        self.assertEqual(self.sent, ['K04', 'K05', 'K06', 'K08', 'K09'])

if __name__=='__main__':unittest.main()
