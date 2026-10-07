import os
import unittest
from pathlib import Path
from unittest.mock import patch
import guoran_desktop as desktop

class PlatformPathTests(unittest.TestCase):
    def test_macos_preferences(self):
        with patch.object(desktop.sys, 'platform', 'darwin'), patch.object(Path, 'home', return_value=Path('/home/test')):
            self.assertEqual(desktop.data_dir(), Path('/home/test/Library/Application Support/GuoranClock'))

    def test_linux_xdg_preferences(self):
        with patch.object(desktop.sys, 'platform', 'linux'), patch.dict(os.environ, {'XDG_CONFIG_HOME': '/custom/config'}):
            self.assertEqual(desktop.data_dir(), Path('/custom/config/GuoranClock'))

    def test_windows_preferences(self):
        with patch.object(desktop.sys, 'platform', 'win32'), patch.dict(os.environ, {'LOCALAPPDATA': '/local'}):
            self.assertEqual(desktop.data_dir(), Path('/local/GuoranClock'))
