import asyncio, queue, sys, unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from bluetooth_backend import Bluetooth
class Char:
    properties=['write-without-response']
    max_write_without_response_size=20
class Client:
    is_connected=True
    def __init__(self): self.writes=[]
    async def write_gatt_char(self, char, data, response): self.writes.append((bytes(data),response))
class TransportTests(unittest.IsolatedAsyncioTestCase):
    def backend(self):
        bt=object.__new__(Bluetooth)
        bt.events=queue.Queue()
        bt.client=Client()
        bt.tx=Char()
        bt.ready=True
        bt.lock=asyncio.Lock()
        return bt
    async def test_long_time_command_and_serial_commands(self):
        bt=self.backend()
        await asyncio.gather(bt.send('$2026-10-03;22:05:03;06'),bt.send('K01'))
        self.assertEqual(bt.client.writes,[(b'$2026-10-03;22:05:03',False),(b';06',False),(b'K01',False)])
    async def test_response_characteristic_keeps_packet(self):
        bt=self.backend()
        bt.tx.properties=['write']
        await bt.send('$2026-10-03;22:05:03;06')
        self.assertEqual(bt.client.writes,[(b'$2026-10-03;22:05:03;06',True)])
    async def test_dual_mode_uses_acknowledged_write(self):
        bt=self.backend()
        bt.tx.properties=['write','write-without-response']
        await bt.send('SB1')
        self.assertEqual(bt.client.writes,[(b'SB1',True)])
    async def test_disconnected_cannot_write(self):
        bt=self.backend()
        bt.ready=False
        with self.assertRaises(RuntimeError): await bt.send('K01')
        self.assertEqual(bt.client.writes,[])
if __name__=='__main__': unittest.main()
