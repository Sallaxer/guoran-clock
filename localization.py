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
