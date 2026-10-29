import asyncio
import sys
import tempfile
import time
import unittest
from datetime import datetime
from pathlib import Path
from unittest.mock import Mock, patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import guoran_desktop as desktop

class ApiTests(unittest.TestCase):
    def setUp(self):
        self.api=desktop.Api()
    def tearDown(self):
        self.api._shutdown()
    def execute(self, coro):
        return asyncio.run_coroutine_threadsafe(coro,self.api._bt.loop).result(timeout=3)
    def test_sent_setting_survives_stale_readback_and_can_be_reversed(self):
        sent=[]
        async def send(command): sent.append(command)
        self.api._bt.send=send
        self.execute(self.api._change('SB1','switches:B',True))
        self.api._events.put(('state',{'switches':{'B':False}}))
        self.assertTrue(self.api.poll()['requested']['switches:B'])
        self.execute(self.api._change('SB0','switches:B',False))
        self.api._events.put(('state',{'switches':{'B':False}}))
        self.assertNotIn('switches:B',self.api.poll()['requested'])
        self.assertEqual(sent,['SB1','SB0'])
    def test_failed_write_does_not_change_requested_state(self):
        async def send(command): raise RuntimeError('Disconnected')
        self.api._bt.send=send
        with self.assertRaises(RuntimeError):
            self.execute(self.api._change('SB1','switches:B',True))
        self.assertEqual(self.api.poll()['requested'],{})
    def run_sync(self, start):
        sent=[]
        async def send(command): sent.append(command)
        async def send_time(): sent.append('TIME' if self.api._sync is False else 'TIME while syncing')
        async def request_state(): return True
        self.api._bt.send=send
        self.api._send_time=send_time
        self.api._bt.request_state=request_state
        with patch.object(desktop,'PAUSE_AFTER_S71',0), patch.object(desktop,'PAUSE_AFTER_STREAM',0), \
             patch.object(desktop,'PAUSE_BEFORE_S70',0):
            self.assertTrue(start()['ok'])
            deadline=time.monotonic()+2
            while self.api.poll()['busy'] and time.monotonic()<deadline: time.sleep(.01)
        return sent
    def test_sync_button_sends_one_lone_time_packet(self):
        # Packets a second apart left the clock 2 s behind; a lone one set it within 0.3 s.
        self.assertEqual(self.run_sync(self.api.sync_time),['S71','TIME','S70'])
    def test_stopping_constant_sync_ends_with_a_lone_packet(self):
        self.api._sync=True
        self.assertEqual(self.run_sync(lambda: self.api.set_auto_sync(False)),['TIME','S70'])
        self.assertFalse(self.api._sync)
        self.assertGreaterEqual(desktop.PAUSE_AFTER_STREAM,3)
    def test_time_is_sent_at_the_next_whole_second(self):
        sent=[]
        async def send(command): sent.append(command)
        self.api._bt.send=send
        clock=Mock(wraps=datetime)
        clock.now.return_value=datetime(2026,10,29,12,0,59,995000)
        with patch.object(desktop,'datetime',clock):
            self.execute(self.api._send_time())
        self.assertEqual(sent,['$2026-10-29;12:01:00;04'])
    def test_theme_persists_and_invalid_theme_is_rejected(self):
        with tempfile.TemporaryDirectory() as temp, patch.object(desktop,'PREFERENCES',Path(temp)/'preferences.json'):
            self.assertTrue(self.api.set_theme('light')['ok'])
            self.assertEqual(self.api.poll()['theme'],'light')
            self.assertFalse(self.api.set_theme('wrong')['ok'])
            another=desktop.Api()
            try: self.assertEqual(another.poll()['theme'],'light')
            finally: another._shutdown()

if __name__=='__main__':unittest.main()
