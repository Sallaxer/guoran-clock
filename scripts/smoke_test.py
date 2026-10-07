"""Launch the packaged UI without Bluetooth and validate its ready state."""
import json
from pathlib import Path
import subprocess
import sys

report = Path('smoke-report.json').resolve()
report.unlink(missing_ok=True)
subprocess.run([str(Path(sys.argv[1]).resolve()), '--smoke-test', str(report)], check=True, timeout=90)
result = json.loads(report.read_text(encoding='utf-8'))
assert 'error' not in result, result
assert result['ready'] and result['visible'], result
assert result['rows'] == 17, result
assert 'Increase' in result['plus'] and 'Decrease' in result['minus'], result
print(json.dumps(result))
