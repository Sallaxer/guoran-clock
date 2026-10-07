import asyncio
import concurrent.futures
import subprocess
import sys
import threading
from bleak import BleakClient, BleakScanner
from protocol import StateBuffer

def uuid(short):
    return f'0000{short}-0000-1000-8000-00805f9b34fb'

class Bluetooth:
    def __init__(self, events):
        self.events = events
        self.loop = asyncio.new_event_loop()
        self.client = None
        self.devices = {}
        self.ready = False
        self.lock = None
        self.buffer = StateBuffer()
        self.state_received = None
        self.last_state = None
        self.thread = threading.Thread(target=self.run, daemon=True)
        self.thread.start()

    def run(self):
        asyncio.set_event_loop(self.loop)
        try:
            self.loop.run_forever()
        finally:
            pending = asyncio.all_tasks(self.loop)
            for task in pending:
                task.cancel()
            if pending:
                self.loop.run_until_complete(asyncio.gather(*pending, return_exceptions=True))
            self.loop.close()

    def emit(self, kind, value):
        self.events.put((kind, value))

    def submit(self, coro, *, release_busy=True):
        future = asyncio.run_coroutine_threadsafe(coro, self.loop)
        def done(f):
            try:
                f.result()
            except (asyncio.CancelledError, concurrent.futures.CancelledError):
                pass
            except Exception as e:
                self.emit('error', str(e))
            finally:
                if release_busy:
                    self.emit('busy', False)
        future.add_done_callback(done)
        return future

    async def scan(self):
        self.emit('status', 'Поиск Bluetooth LE устройств…')
        results = await BleakScanner.discover(timeout=10, return_adv=True)
        self.devices = {d.address: d for d,a in results.values()}
        rows = [{'address':d.address, 'name':a.local_name or d.name or 'Без имени',
                 'rssi':a.rssi, 'likely':(a.local_name or d.name or '').startswith('XGGF')}
                for d,a in results.values()]
        rows.sort(key=lambda r:(not r['likely'], -r['rssi']))
        self.emit('devices', rows)
        self.emit('status', f'Найдено устройств: {len(rows)}. Выберите часы XGGF.')

    async def radio(self):
        if sys.platform == 'win32':
            await self.radio_windows()
        elif sys.platform == 'darwin':
            # macOS has no public API to power the radio; send the user to Settings.
            subprocess.Popen(['open', 'x-apple.systempreferences:com.apple.BluetoothSettings'])
            self.emit('status', 'Включите Bluetooth в открывшихся настройках macOS')
        else:
            await self.radio_bluez()

    async def radio_bluez(self):
        from dbus_fast import BusType, DBusError, Variant
        from dbus_fast.aio import MessageBus
        bus = await MessageBus(bus_type=BusType.SYSTEM).connect()
        try:
            root = bus.get_proxy_object('org.bluez', '/', await bus.introspect('org.bluez', '/'))
            objects = await root.get_interface('org.freedesktop.DBus.ObjectManager').call_get_managed_objects()
            adapters = [path for path, interfaces in objects.items() if 'org.bluez.Adapter1' in interfaces]
            if not adapters:
                raise RuntimeError('Bluetooth-адаптер не найден')
            for path in adapters:
                if objects[path]['org.bluez.Adapter1']['Powered'].value:
                    continue
                adapter = bus.get_proxy_object('org.bluez', path, await bus.introspect('org.bluez', path))
                try:
                    await adapter.get_interface('org.freedesktop.DBus.Properties').call_set(
                        'org.bluez.Adapter1', 'Powered', Variant('b', True))
                except DBusError as e:
                    raise RuntimeError(f'Linux не разрешил включить Bluetooth ({e.text}). Проверьте rfkill и настройки системы.')
        except DBusError as e:
            raise RuntimeError(f'BlueZ недоступен ({e.text})')
        finally:
            bus.disconnect()
        self.emit('status', 'Bluetooth включён')

    async def radio_windows(self):
        from winrt.windows.devices.radios import Radio, RadioKind, RadioState
        radios = [r for r in await Radio.get_radios_async() if r.kind == RadioKind.BLUETOOTH]
        if not radios:
            raise RuntimeError('Bluetooth-адаптер не найден')
        for r in radios:
            if r.state != RadioState.ON:
                result = await r.set_state_async(RadioState.ON)
                if r.state != RadioState.ON:
                    raise RuntimeError(f'Windows не разрешила включить Bluetooth ({result}). Включите его в параметрах Windows.')
        self.emit('status', 'Bluetooth включён')

    def dropped(self, client):
        if client is self.client:
            self.ready = False
            self.emit('ready', False)
            self.emit('status', 'Соединение закрыто')

    def notification(self, sender, data):
        self.emit('log', 'RX ' + bytes(data).hex(' '))
        for state in self.buffer.feed(data):
            self.last_state = state
            if self.state_received:
                self.state_received.set()
            self.emit('state', state)

    async def request_state(self, attempts=3, timeout=1.5):
        if not self.ready:
            raise RuntimeError('Сначала подключитесь к часам')
        self.state_received.clear()
        self.emit('status', 'Читаю настройки часов…')
        for attempt in range(attempts):
            await self.send('OSC')
            try:
                await asyncio.wait_for(self.state_received.wait(), timeout=timeout)
                self.emit('status', 'Настройки получены от часов')
                return True
            except asyncio.TimeoutError:
                pass
        self.emit('status', 'Соединение есть, но ответа с настройками пока нет. Повторите чтение.')
        return False

    async def connect(self, address, password):
        if len(password)!=6 or not password.isascii() or not password.isdigit():
            raise ValueError('Пароль должен содержать 6 цифр')
        await self.disconnect()
        self.emit('status', 'Подключение и проверка протокола…')
        client = BleakClient(self.devices[address], disconnected_callback=self.dropped,
                             timeout=20, winrt={'use_cached_services':False})
        self.client = client
        self.lock = asyncio.Lock()
        self.buffer = StateBuffer()
        self.last_state = None
        self.state_received = asyncio.Event()
        try:
            await client.connect()
            for service in client.services:
                self.emit('log', 'GATT '+service.uuid+' '+', '.join(c.uuid+' '+str(c.properties) for c in service.characteristics))
            self.tx = client.services.get_characteristic(uuid('ffe9'))
            rx = client.services.get_characteristic(uuid('ffe4'))
            if not self.tx or not rx or self.tx.service_uuid != uuid('ffe5') or rx.service_uuid != uuid('ffe0'):
                raise RuntimeError('Устройство не соответствует протоколу guoran.apk (FFE5/FFE9, FFE0/FFE4)')
            await client.start_notify(rx, self.notification)
            auth = client.services.get_characteristic(uuid('ffc1'))
            auth_rx = client.services.get_characteristic(uuid('ffc2'))
            if auth:
                if not auth_rx:
                    raise RuntimeError('Отсутствует ответ авторизации FFC2')
                result = self.loop.create_future()
                def auth_response(sender, data):
                    self.emit('log', 'AUTH RX '+bytes(data).hex(' '))
                    if not result.done():
                        result.set_result(bytes(data))
                await client.start_notify(auth_rx, auth_response)
                # Repeat the existing password: never provision/change a device password.
                await self.write(auth, (password+password).encode('ascii'))
                reply = await asyncio.wait_for(result, timeout=10)
                if reply not in (b'\x00', b'\x02'):
                    raise RuntimeError('Часы отклонили пароль. Введите действующий пароль подключения.')
            self.ready = True
            self.emit('ready', True)
            await self.request_state()
        except BaseException:
            await self.disconnect()
            raise

    async def write(self, characteristic, payload):
        response = 'write' in characteristic.properties
        size = 512 if response else max(1, characteristic.max_write_without_response_size)
        for i in range(0, len(payload), size):
            await asyncio.wait_for(self.client.write_gatt_char(characteristic, payload[i:i+size], response=response), timeout=8)
            if i+size < len(payload):
                await asyncio.sleep(0.05)

    async def send(self, command):
        if not self.ready or not self.client or not self.client.is_connected:
            raise RuntimeError('Сначала подключитесь к часам')
        async with self.lock:
            await self.write(self.tx, command.encode('ascii'))
            self.emit('log', 'TX '+command)
            await asyncio.sleep(0.08)

    async def disconnect(self):
        self.ready = False
        self.emit('ready', False)
        if self.client:
            await self.client.disconnect()
        self.client = None

