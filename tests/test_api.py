import asyncio
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
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
    def test_theme_persists_and_invalid_theme_is_rejected(self):
        with tempfile.TemporaryDirectory() as temp, patch.object(desktop,'PREFERENCES',Path(temp)/'preferences.json'):
            self.assertTrue(self.api.set_theme('light')['ok'])
            self.assertEqual(self.api.poll()['theme'],'light')
            self.assertFalse(self.api.set_theme('wrong')['ok'])
            another=desktop.Api()
            try: self.assertEqual(another.poll()['theme'],'light')
            finally: another._shutdown()

if __name__=='__main__':unittest.main()
