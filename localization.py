"""Translate application status without changing raw protocol diagnostics."""
import re
MESSAGES = {
    'Подключите часы, чтобы начать': 'Connect your clock to begin',
    'Часы не подключены': 'Clock not connected',
    'Часы отключены': 'Clock disconnected',
    'Соединение закрыто': 'Connection closed',
    'Поиск Bluetooth LE устройств…': 'Searching for Bluetooth LE devices…',
    'Bluetooth включён': 'Bluetooth is on',
    'Bluetooth-адаптер не найден': 'Bluetooth adapter not found',
    'Включите Bluetooth в открывшихся настройках macOS': 'Turn on Bluetooth in the macOS Settings window that opened',
    'Подключение и проверка протокола…': 'Connecting and checking the protocol…',
    'Читаю настройки часов…': 'Reading clock settings…',
    'Синхронизирую время…': 'Synchronizing time…',
    'Настройки получены от часов': 'Settings received from the clock',
    'Соединение есть, но ответа с настройками пока нет. Повторите чтение.': 'Connected, but no settings reply received. Try reading again.',
    'Повторный запрос без ответа. Переподключаюсь для чтения настроек…': 'No reply. Reconnecting to read settings…',
    'Команда передана. Подтверждения настройки от часов пока нет.': 'Command sent. The clock has not confirmed the setting yet.',
    'Сначала подключитесь к часам': 'Connect to the clock first',
    'Сначала найдите и выберите часы': 'Search for and select a clock first',
    'Дождитесь завершения текущей операции': 'Wait for the current operation to finish',
    'Пароль должен содержать 6 цифр': 'The password must contain 6 digits',
    'Часы отклонили пароль. Введите действующий пароль подключения.': 'The clock rejected the password. Enter its current connection password.',
    'Неверный переключатель': 'Invalid switch',
    'Неверный цвет': 'Invalid color',
    'Неверная кнопка': 'Invalid button',
    'Неверное значение': 'Invalid value',
    'Неизвестная тема': 'Unknown theme',
    'Введите время в формате ЧЧ:ММ, например 07:30': 'Enter a valid time in HH:MM format, e.g. 07:30',
    'Отсутствует ответ авторизации FFC2': 'Authorization response channel FFC2 is missing',
    'Устройство не соответствует протоколу guoran.apk (FFE5/FFE9, FFE0/FFE4)': 'Device does not support the Guoran protocol (FFE5/FFE9, FFE0/FFE4)',
}
def translate(message, language):
    if language == "zh-CN":
        return translate_chinese(message)
    if language != 'en' or not message:
        return message
    if message in MESSAGES:
        return MESSAGES[message]
    match = re.fullmatch(r'Найдено устройств: (\d+)\. Выберите часы XGGF\.', message)
    if match:
        return f'Found {match[1]} devices. Select the XGGF clock.'
    if message.startswith('Ошибка: '):
        return 'Error: '+translate(message[8:], language)
    if message.startswith('Windows не разрешила включить Bluetooth'):
        return 'Windows could not turn on Bluetooth. Enable it in Windows Settings.'
    if message.startswith('Linux не разрешил включить Bluetooth'):
        return 'Linux could not turn on Bluetooth. Check rfkill and system settings.'
    if message.startswith('BlueZ недоступен'):
        return 'BlueZ is not available'+message[len('BlueZ недоступен'):]
    return message
ZH_MESSAGES = {
 'Connect your clock to begin':'请连接时钟以开始使用',
 'Clock not connected':'时钟未连接','Clock disconnected':'时钟已断开','Connection closed':'连接已关闭',
 'Searching for Bluetooth LE devices…':'正在搜索低功耗蓝牙设备…','Bluetooth is on':'蓝牙已开启','Bluetooth adapter not found':'未找到蓝牙适配器',
 'Turn on Bluetooth in the macOS Settings window that opened':'请在已打开的 macOS 设置窗口中开启蓝牙',
 'Connecting and checking the protocol…':'正在连接并检查协议…','Reading clock settings…':'正在读取时钟设置…','Synchronizing time…':'正在同步时间…','Settings received from the clock':'已收到时钟设置',
 'Connected, but no settings reply received. Try reading again.':'已连接，但尚未收到设置回复。请重试读取。',
 'No reply. Reconnecting to read settings…':'未收到回复。正在重新连接以读取设置…',
 'Command sent. The clock has not confirmed the setting yet.':'命令已发送，时钟尚未确认设置。',
 'Connect to the clock first':'请先连接时钟','Search for and select a clock first':'请先查找并选择时钟','Wait for the current operation to finish':'请等待当前操作完成',
 'The password must contain 6 digits':'密码必须为 6 位数字','The clock rejected the password. Enter its current connection password.':'时钟拒绝了密码。请输入当前连接密码。',
 'Invalid switch':'无效的开关','Invalid color':'无效的颜色','Invalid button':'无效的按键','Invalid value':'无效的值','Unknown theme':'未知主题',
 'Enter a valid time in HH:MM format, e.g. 07:30':'请按 HH:MM 格式输入有效时间，例如 07:30',
 'Authorization response channel FFC2 is missing':'缺少授权回复通道 FFC2',
 'Device does not support the Guoran protocol (FFE5/FFE9, FFE0/FFE4)':'设备不支持 Guoran 协议（FFE5/FFE9、FFE0/FFE4）',
 'Invalid language':'无效的语言','Invalid schedule state':'无效的定时开关状态'
}

def translate_chinese(message):
    if not message:
        return message
    if message in ZH_MESSAGES:
        return ZH_MESSAGES[message]
    if message in MESSAGES:
        return ZH_MESSAGES.get(MESSAGES[message], message)
    match = re.fullmatch(r'Найдено устройств: (\d+)\. Выберите часы XGGF\.', message)
    if match:
        return f'找到 {match[1]} 个设备。请选择 XGGF 时钟。'
    if message.startswith('Ошибка: '):
        return '错误：'+translate_chinese(message[8:])
    if message.startswith('Windows не разрешила включить Bluetooth'):
        return 'Windows 无法开启蓝牙。请在 Windows 设置中开启。'
    if message.startswith('Linux не разрешил включить Bluetooth'):
        return 'Linux 无法开启蓝牙。请检查 rfkill 和系统设置。'
    if message.startswith('BlueZ недоступен'):
        return 'BlueZ 不可用'+message[len('BlueZ недоступен'):]
    return message
