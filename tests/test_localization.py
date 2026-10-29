import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import guoran_desktop as desktop
from localization import MESSAGES, ZH_MESSAGES, translate

ROOT = Path(__file__).resolve().parents[1]

class LocalizationTests(unittest.TestCase):
    def test_chinese_covers_backend_messages(self):
        for russian, english in MESSAGES.items():
            self.assertIn(english, ZH_MESSAGES)
            self.assertEqual(translate(russian, 'zh-CN'), ZH_MESSAGES[english])
        self.assertEqual(translate('Найдено устройств: 3. Выберите часы XGGF.', 'zh-CN'), '找到 3 个设备。请选择 XGGF 时钟。')
        self.assertEqual(translate('Синхронизирую время…', 'en'), 'Synchronizing time…')
        self.assertEqual(translate('TX $2026-10-29', 'zh-CN'), 'TX $2026-10-29')

    def test_chinese_preference_survives_restart(self):
        with tempfile.TemporaryDirectory() as temp, patch.object(desktop, 'PREFERENCES', Path(temp)/'preferences.json'):
            api = desktop.Api()
            try:
                self.assertTrue(api.set_language('zh-CN')['ok'])
                self.assertFalse(api.set_language('invalid')['ok'])
            finally:
                api._shutdown()
            api = desktop.Api()
            try:
                self.assertEqual(api.poll()['language'], 'zh-CN')
            finally:
                api._shutdown()

    @unittest.skipUnless(shutil.which('node'), 'Node is required for UI dictionary validation')
    def test_ui_dictionary_completeness_and_placeholders(self):
        source = (ROOT/'ui/i18n.js').read_text(encoding='utf-8')+'\n'+(ROOT/'ui/zh.js').read_text(encoding='utf-8')
        source += r'''
const assert = require('node:assert/strict');
const slots = s => [...s.matchAll(/\{\w+\}/g)].map(m=>m[0]).sort();
for(const [key,texts] of Object.entries(messages)){
 assert.equal(texts.length,3,key);
 for(const text of texts){ assert.ok(text,key); assert.deepEqual(slots(text), slots(texts[0]),key); }
}
for(const row of menuRows){assert.equal(row[1].length,3);assert.equal(row[2].length,3);}
language='zh-CN';assert.equal(t('channel',{n:2}),'通道 2');
language='ru';assert.equal(t('plus'),'Увеличить');assert.equal(t('minus'),'Уменьшить');
language='en';assert.equal(t('plus'),'Increase');
'''
        subprocess.run(['node','-e',source],check=True,capture_output=True,text=True,encoding='utf-8')
