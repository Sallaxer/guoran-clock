"""Protocol recovered from guoran.apk assets/apps/H5DD29EBE/www/js/index.js."""
import re
from datetime import datetime

SWITCHES = [(str(i), f'Лампа {i}') for i in range(1, 7)] + [
    ('7', 'Синхронизация времени'), ('8', 'Будильник 1'), ('9', 'Будильник 2'),
    ('0', 'Включение по расписанию'), ('A', 'Автоматическая яркость'),
    ('B', '12-часовой формат'), ('C', 'Датчик освещения'),
    ('D', 'Голосовое сообщение каждый час'), ('E', 'Английский язык'),
    ('F', 'Сенсорное включение')]

def rgb_command(rgb):
    if len(rgb) != 3 or any(not 0 <= n <= 255 for n in rgb):
        raise ValueError('RGB должен быть в пределах 0–255')
    return 'R%03d-G%03d-B%03d' % tuple(rgb)

def time_command(kind, value):
    if not re.fullmatch(r'(?:[01]\d|2[0-3]):[0-5]\d', value):
        raise ValueError('Введите время в формате ЧЧ:ММ, например 07:30')
    prefix, suffix = {'alarm1': ('A','A'), 'alarm2': ('A','B'),
                      'on': ('T','O'), 'off': ('T','C')}[kind]
    return prefix + value + suffix

def system_time(now=None):
    now = now or datetime.now()
    return now.strftime('$%Y-%m-%d;%H:%M:%S;') + f'0{(now.weekday()+1)%7}'

def parse_state(frame):
    if len(frame) != 93 or not frame.endswith('CSS'):
        raise ValueError('Неполный пакет настроек')
    rgb = re.fullmatch(r'R(\d{3})-G(\d{3})-B(\d{3})', frame[:14])
    if not rgb or any(int(v)>255 for v in rgb.groups()):
        raise ValueError('Неверный RGB')
    switches = {}
    raw_switches = {}
    for i, (key, _) in enumerate(SWITCHES):
        value = frame[14+i*3:17+i*3]
        if len(value) != 3 or value[:2] != 'S'+key or not 32 <= ord(value[2]) < 127:
            raise ValueError('Неверный переключатель')
        raw_switches[key] = value[-1]
        switches[key] = {'0': False, '1': True}.get(value[-1])
    times = {}
    raw_times = {}
    for i, kind in enumerate(['alarm1','alarm2','on','off']):
        value = frame[62+i*7:69+i*7]
        prefix,suffix={'alarm1':('A','A'),'alarm2':('A','B'),'on':('T','O'),'off':('T','C')}[kind]
        if not re.fullmatch(prefix+r'\d{2}:\d{2}'+suffix, value):
            raise ValueError('Неверный пакет времени')
        raw_times[kind] = value[1:6]
        try:
            time_command(kind,value[1:6])
            times[kind] = value[1:6]
        except ValueError:
            times[kind] = None
    return {'rgb': tuple(map(int, rgb.groups())), 'switches': switches,
            'raw_switches': raw_switches, 'times': times, 'raw_times': raw_times}

class StateBuffer:
    """Notifications may split the 93-byte snapshot into arbitrary chunks."""
    def __init__(self):
        self.buffer = ''
    def feed(self, data):
        self.buffer += bytes(data).decode('ascii', errors='replace')
        states = []
        while len(self.buffer) >= 93:
            start = self.buffer.find('R')
            if start < 0:
                self.buffer = ''
                break
            self.buffer = self.buffer[start:]
            if len(self.buffer) < 93:
                break
            try:
                state = parse_state(self.buffer[:93])
            except ValueError:
                self.buffer = self.buffer[1:]
            else:
                states.append(state)
                self.buffer = self.buffer[93:]
        self.buffer = self.buffer[-512:]
        return states
