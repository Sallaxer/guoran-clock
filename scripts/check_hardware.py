"""Explicit opt-in hardware check; changes color then restores supplied original color."""
import argparse,json,sys,time
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from guoran_desktop import Api
p=argparse.ArgumentParser()
p.add_argument('--device',required=True)
p.add_argument('--password',default='210709')
p.add_argument('--test-color',required=True)
p.add_argument('--restore-color',required=True)
p.add_argument('--output',required=True)
args=p.parse_args()
api=Api();results={}
def wait():
    deadline=time.monotonic()+45
    while time.monotonic()<deadline:
        s=api.poll()
        if not s['busy']:
            if s['error']:raise RuntimeError(s['error'])
            return s
        time.sleep(.1)
    raise TimeoutError('Operation timeout')
try:
    api.scan();s=wait()
    d=next(d for d in s['devices'] if d['name']==args.device)
    api.connect(d['address'],args.password);s=wait()
    results['before']=s['snapshot']
    try:
        api.set_color(args.test_color);wait();time.sleep(1)
        api.refresh();s=wait()
        results['test']=s['snapshot']
        print('TEST',json.dumps(s['snapshot']),flush=True)
    finally:
        api.set_color(args.restore_color);wait();time.sleep(1)
        api.refresh();s=wait()
        results['restored']=s['snapshot']
        print('RESTORED',json.dumps(s['snapshot']),flush=True)
finally:
    results['logs']=api.poll()['logs']
    Path(args.output).write_text(json.dumps(results,ensure_ascii=False,indent=2),encoding='utf-8')
    api._shutdown()
