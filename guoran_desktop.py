"""Guoran 2: local WebView UI and native BLE transport (Windows, macOS, Linux)."""
import asyncio
import copy
import json
import os
import queue
import re
import subprocess
import sys
import threading
import traceback
from datetime import datetime
from pathlib import Path

from bluetooth_backend import Bluetooth
from protocol import SWITCHES, rgb_command, system_time, time_command
from localization import MESSAGES, translate

RESOURCES = Path(getattr(sys, '_MEIPASS', Path(__file__).parent))
BASE = Path(sys.executable).parent if getattr(sys, 'frozen', False) else Path(__file__).parent

def data_dir():
    if sys.platform == 'win32':
        return Path(os.environ.get('LOCALAPPDATA', str(BASE))) / 'GuoranClock'
    if sys.platform == 'darwin':
        return Path.home() / 'Library' / 'Application Support' / 'GuoranClock'
    return Path(os.environ.get('XDG_CONFIG_HOME') or Path.home() / '.config') / 'GuoranClock'

def output_dir():
    # A macOS .app bundle or a Linux install dir is not a place for user files.
    if sys.platform == 'win32':
        return BASE
    if sys.platform == 'darwin':
        # ~/Downloads is TCC-protected; writing there fails without a consent prompt.
        path = Path.home() / 'Library' / 'Logs' / 'GuoranClock'
        path.mkdir(parents=True, exist_ok=True)
        return path
    downloads = Path.home() / 'Downloads'
    return downloads if downloads.is_dir() else Path.home()

PREFERENCES = data_dir() / 'preferences.json'

class Api:
    def __init__(self):
        self._events = queue.Queue()
        self._bt = Bluetooth(self._events)
        self._mutex = threading.Lock()
        self._operation_lock = threading.Lock()
        self._revision = 0
        self._sync = False
        self._closing = False
        self._connection = None
        self._state = {'connected':False, 'busy':False, 'status':'Подключите часы, чтобы начать',
                       'devices':[], 'device_name':'Часы не подключены', 'snapshot':None,
                       'snapshot_at':None, 'logs':[], 'auto_sync':False, 'version':'2.4.0', 'error':None,
                       'theme': 'dark', 'language': 'ru', 'schedule': {'on': '', 'off': ''},
                       'requested': {}, 'last_command': None}
        self._preferences_lock = threading.Lock()
        try:
            prefs = json.loads(PREFERENCES.read_text(encoding='utf-8'))
            theme = prefs.get('theme')
            if theme in ('light', 'dark'):
                self._state['theme'] = theme
            if prefs.get('language') in ('ru', 'en'):
                self._state['language'] = prefs['language']
            for kind in ('on', 'off'):
                value = prefs.get('schedule', {}).get(kind, '')
                if re.fullmatch(r'(?:[01]\d|2[0-3]):[0-5]\d', str(value)):
                    self._state['schedule'][kind] = value
        except (OSError, ValueError, AttributeError):
            pass
        self._sync_future = asyncio.run_coroutine_threadsafe(self._sync_loop(), self._bt.loop)

    def _log(self, message):
        line=datetime.now().strftime('%H:%M:%S ')+message
        self._state['logs'].append(line)
        self._state['logs']=self._state['logs'][-1000:]

    def poll(self):
        with self._mutex:
            while not self._events.empty():
                kind,value=self._events.get_nowait()
                self._revision+=1
                if kind=='state':
                    self._state['snapshot']=value
                    self._state['snapshot_at']=datetime.now().strftime('%H:%M:%S')
                    # Only an exact readback confirms a requested value.
                    for field, requested in list(self._state['requested'].items()):
                        group, _, key = field.partition(':')
                        actual = value.get(group) if not key else value.get(group, {}).get(key)
                        if actual == requested or (group == 'rgb' and list(actual or []) == list(requested)):
                            del self._state['requested'][field]
                elif kind=='ready':
                    self._state['connected']=value
                    if not value:
                        self._sync=False
                        self._state['auto_sync']=False
                elif kind=='devices':
                    self._state['devices']=value
                elif kind=='status':
                    self._state['status']=value
                    self._log(value)
                elif kind=='error':
                    self._state['error']=value
                    self._state['status']='Ошибка: '+value
                    self._log('ОШИБКА '+value)
                elif kind=='log':
                    self._log(value)
            self._state['busy']=self._operation_lock.locked()
            self._state['auto_sync']=self._sync
            self._state['revision']=self._revision
            result = copy.deepcopy(self._state)
            for key in ('status', 'error', 'device_name'):
                result[key] = translate(result[key], result['language'])
            return result

    def _run(self,coro):
        if not self._operation_lock.acquire(blocking=False):
            coro.close()
            return {'ok':False,'error':'Дождитесь завершения текущей операции'}
        with self._mutex:
            self._state['error']=None
        future=asyncio.run_coroutine_threadsafe(coro,self._bt.loop)
        def done(f):
            try:
                f.result()
            except Exception as e:
                self._events.put(('error',str(e) or type(e).__name__))
            finally:
                self._operation_lock.release()
        future.add_done_callback(done)
        return {'ok':True}

    def scan(self):
        return self._run(self._bt.scan())

    def set_theme(self, theme):
        if theme not in ('light', 'dark'):
            return {'ok': False, 'error': 'Неизвестная тема'}
        return self._save_preferences(theme=theme)

    def _save_preferences(self, **changes):
        with self._preferences_lock:
            with self._mutex:
                prefs = {k: copy.deepcopy(self._state[k]) for k in ('theme', 'language', 'schedule')}
            prefs.update(changes)
            try:
                PREFERENCES.parent.mkdir(parents=True, exist_ok=True)
                temporary = PREFERENCES.with_suffix('.tmp')
                temporary.write_text(json.dumps(prefs, ensure_ascii=False), encoding='utf-8')
                temporary.replace(PREFERENCES)
            except OSError as e:
                return {'ok': False, 'error': str(e)}
            with self._mutex:
                self._state.update(prefs)
        return {'ok': True}

    def set_language(self, language):
        if language not in ('ru', 'en'):
            return {'ok': False, 'error': 'Invalid language'}
        return self._save_preferences(language=language)

    def save_schedule(self, on, off):
        try:
            # Empty fields may be saved as drafts, but cannot be sent.
            for kind, value in (('on', on), ('off', off)):
                if value != '':
                    time_command(kind, value)
        except (TypeError, ValueError) as e:
            return {'ok': False, 'error': str(e)}
        return self._save_preferences(schedule={'on': on, 'off': off})

    def apply_schedule(self, on, off, enabled):
        if type(enabled) is not bool:
            return {'ok': False, 'error': 'Invalid schedule state'}
        try:
            commands = [time_command('on', on), time_command('off', off)] if enabled else []
        except (ValueError, TypeError) as e:
            return {'ok': False, 'error': str(e)}
        async def apply():
            # Validate both values before any write; enable only after both succeeded.
            for command, kind, value in zip(commands, ('on', 'off'), (on, off)):
                await self._change(command, 'times:'+kind, value)
            await self._change('S0'+str(int(enabled)), 'switches:0', enabled)
        return self._run(apply())

    def enable_bluetooth(self):
        return self._run(self._bt.radio())

    def connect(self,address,password):
        if address not in self._bt.devices:
            return {'ok':False,'error':'Сначала найдите и выберите часы'}
        async def connect():
            self._sync=False
            with self._mutex:
                self._state['snapshot']=None
                self._state['snapshot_at']=None
                self._state['requested']={}
                self._state['device_name']=self._bt.devices[address].name or address
            await self._bt.connect(address,str(password))
            self._connection = (address,str(password))
        return self._run(connect())

    def disconnect(self):
        self._sync=False
        self._connection=None
        async def disconnect():
            await self._bt.disconnect()
            self._events.put(('status','Часы отключены'))
        return self._run(disconnect())

    def refresh(self):
        async def refresh():
            if await self._bt.request_state(attempts=1, timeout=1):
                return
            if self._connection:
                self._events.put(('status','Повторный запрос без ответа. Переподключаюсь для чтения настроек…'))
                self._sync=False
                await self._bt.disconnect()
                await asyncio.sleep(2)
                await self._bt.connect(*self._connection)
        return self._run(refresh())

    async def _change(self, command, field=None, value=None):
        await self._bt.send(command)
        with self._mutex:
            self._state['last_command'] = command
            if field:
                self._state['requested'][field] = value
        self._events.put(('status', 'Команда передана. Подтверждения настройки от часов пока нет.'))

    def set_switch(self,key,enabled):
        if key not in {k for k,_ in SWITCHES} or type(enabled) is not bool:
            return {'ok':False,'error':'Неверный переключатель'}
        return self._run(self._change('S'+key+str(int(enabled)), 'switches:'+key, enabled))

    def set_color(self,color):
        if not isinstance(color,str) or not re.fullmatch(r'#[0-9a-fA-F]{6}',color):
            return {'ok':False,'error':'Неверный цвет'}
        rgb=tuple(int(color[i:i+2],16) for i in (1,3,5))
        return self._run(self._change(rgb_command(rgb), 'rgb', list(rgb)))

    def set_time(self,kind,value):
        try:
            command=time_command(kind,value)
        except (KeyError,ValueError,TypeError) as e:
            return {'ok':False,'error':str(e)}
        return self._run(self._change(command, 'times:'+kind, value))

    def remote_key(self,key):
        if key not in [f'K{i:02}' for i in range(1,10)]:
            return {'ok':False,'error':'Неверная кнопка'}
        if key == 'K07':
            async def enter_menu():
                # This clock needs Back before SET (observed by its owner).
                # Keep both writes in one operation; never toggle power here.
                await self._change('K05')
                await asyncio.sleep(0.25)
                await self._change('K07')
            return self._run(enter_menu())
        return self._run(self._change(key))

    def sync_time(self):
        async def sync():
            await self._bt.send('S71')
            await self._bt.send(system_time())
            if not self._sync:
                await self._bt.send('S70')
            await self._bt.request_state()
        return self._run(sync())

    def set_auto_sync(self,enabled):
        if type(enabled) is not bool:
            return {'ok':False,'error':'Неверное значение'}
        async def change():
            await self._bt.send('S7'+str(int(enabled)))
            self._sync=enabled
            if enabled:
                await self._bt.send(system_time())
            await self._bt.request_state()
        return self._run(change())

    async def _sync_loop(self):
        while not self._closing:
            await asyncio.sleep(1)
            if self._sync and self._bt.ready and not self._operation_lock.locked():
                try:
                    await self._bt.send(system_time())
                except Exception as e:
                    self._sync=False
                    self._events.put(('error',str(e)))

    def save_log(self):
        state=self.poll()
        try:
            path=output_dir()/'guoran-diagnostics.txt'
            path.write_text('Guoran Clock 2.4.0\n'+ '\n'.join(state['logs'])+
                            '\n\nПоследний ответ:\n'+json.dumps(state['snapshot'],ensure_ascii=False,indent=2),encoding='utf-8')
            if sys.platform == 'darwin':
                subprocess.Popen(['open', '-R', str(path)])
            return {'ok':True,'path':str(path)}
        except OSError as e:
            return {'ok':False,'error':str(e)}

    def _shutdown(self):
        self._closing=True
        self._sync=False
        self._sync_future.cancel()
        try:
            asyncio.run_coroutine_threadsafe(self._bt.disconnect(),self._bt.loop).result(timeout=4)
        except Exception:
            pass
        self._bt.loop.call_soon_threadsafe(self._bt.loop.stop)
        self._bt.thread.join(timeout=2)

def main():
    import webview
    if '--smoke-test' in sys.argv:
        import logging
        handler = logging.FileHandler('smoke-webview.log', encoding='utf-8')
        logging.getLogger('pywebview').addHandler(handler)
        logging.getLogger('pywebview').setLevel(logging.DEBUG)
    if sys.platform == 'win32':
        try:
            import ctypes
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID('Guoran.Clock.Desktop.2')
        except Exception:
            pass
    api=Api()
    html=(RESOURCES/'ui'/'index.html').read_text(encoding='utf-8')
    html=html.replace('/*__CSS__*/',(RESOURCES/'ui'/'app.css').read_text(encoding='utf-8'))
    html=html.replace('/*__JS__*/',(RESOURCES/'ui'/'i18n.js').read_text(encoding='utf-8')+'\n'+(RESOURCES/'ui'/'app.js').read_text(encoding='utf-8'))
    html=html.replace('/*__ERRORS__*/{}',json.dumps(MESSAGES,ensure_ascii=False))
    import base64
    icon=RESOURCES/'ui'/'clock-ui.png'
    html=html.replace('__CLOCK_ICON__','data:image/png;base64,'+base64.b64encode(icon.read_bytes()).decode() if icon.exists() else '')
    window=webview.create_window('Guoran Clock',html=html,js_api=api,
        width=1180,height=860,min_size=(880,660),background_color='#191714',text_select=True)
    window.events.closed+=api._shutdown
    try:
        # None picks Cocoa WebKit on macOS and GTK or Qt on Linux.
        smoke = None
        if '--smoke-test' in sys.argv:
            report = Path(sys.argv[sys.argv.index('--smoke-test') + 1]).resolve()
            def smoke():
                import time
                try:
                    if not window.events.loaded.wait(60):
                        raise RuntimeError('Page load timed out; shown=' + str(window.events.shown.is_set()))
                    deadline = time.monotonic() + 60
                    while time.monotonic() < deadline:
                        if window.evaluate_js("typeof apiReady !== 'undefined' && apiReady"):
                            break
                        time.sleep(.2)
                    else:
                        raise RuntimeError('WebView API did not initialize')
                    result = window.evaluate_js("""JSON.stringify((()=>{
                        applyLanguage('en');openMenuReference();
                        return {ready:apiReady, rows:document.querySelectorAll('#remote-menu-table tr').length,
                            visible:!document.querySelector('#remote-reference').hidden,
                            plus:document.querySelector('[data-key="K06"]').textContent.trim(),
                            minus:document.querySelector('[data-key="K09"]').textContent.trim()};
                    })())""")
                    report.write_text(result, encoding='utf-8')
                except Exception:
                    report.write_text(json.dumps({'error': traceback.format_exc()}), encoding='utf-8')
                finally:
                    window.destroy()
        webview.start(smoke, gui='edgechromium' if sys.platform == 'win32' else None,private_mode=True)
    except Exception:
        (output_dir()/'guoran-startup-error.txt').write_text(traceback.format_exc(),encoding='utf-8')
        raise

if __name__=='__main__':
    main()
