"""Offline one-shot state machine test; no real bandwidth tests or network."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import time

ROOT = Path(__file__).resolve().parents[1]
script = (ROOT/'src/manual_run.py').read_text()
assert "'/var/run/opnsense-librespeed-manual.lock'" in script
assert 'subprocess.Popen' in script
assert 'flock' in script
assert 'start_new_session=True' in script
assert 'subprocess.run([str(MEASURE)]' in script

with tempfile.TemporaryDirectory() as d:
    base = Path(d)
    for success in (True, False):
        stem = 'success' if success else 'failed'
        measure = base / (stem+'-measure.sh')
        measure.write_text(f'#!/bin/sh\nsleep 1\nexit {0 if success else 1}\n')
        measure.chmod(0o755)
        runner = base / (stem+'-runner.py')
        modified = script.replace('/var/run/opnsense-librespeed-manual.lock', str(base/(stem+'-manual.lock')))
        modified = modified.replace('/var/run/opnsense-librespeed-manual.json',str(base/(stem+'-manual.json')))
        modified = modified.replace('/usr/local/opnsense/scripts/csvspeedtest/measure.sh',str(measure))
        modified = modified.replace('/var/run/opnsense-librespeed.lock',str(base/(stem+'-measure.lock')))
        modified = modified.replace("LOCKF = '/usr/bin/lockf'", "LOCKF = '/usr/bin/true'")
        runner.write_text(modified)
        def call(action):
            res=subprocess.run([sys.executable,str(runner),action],capture_output=True,text=True,timeout=10)
            assert res.returncode==0,(res.returncode,res.stdout,res.stderr)
            return json.loads(res.stdout)
        assert call('status')['status']=='idle'
        start=call('start')
        assert start['status']=='starting', start
        second=call('start')
        assert second['status']=='running', second
        deadline=time.monotonic()+8
        while time.monotonic()<deadline:
            last=call('status')
            if last['status'] in ('done','failed'): break
            time.sleep(0.1)
        assert last['status']==('done' if success else 'failed'),last
        assert last['token']==start['token']
        assert last.get('finished')
        print('manual test',stem,'OK')

# A concurrent Cron/CLI measurement must block a new manual launch.
with tempfile.TemporaryDirectory() as d:
    base = Path(d)
    measure = base / 'measure.sh'
    measure.write_text('#!/bin/sh\nexit 0\n')
    measure.chmod(0o755)
    busy = base / 'busy-lockf'
    busy.write_text('#!/bin/sh\nexit 1\n')
    busy.chmod(0o755)
    runner = base / 'runner.py'
    modified = script.replace('/var/run/opnsense-librespeed-manual.lock', str(base/'manual.lock'))
    modified = modified.replace('/var/run/opnsense-librespeed-manual.json', str(base/'manual.json'))
    modified = modified.replace('/usr/local/opnsense/scripts/csvspeedtest/measure.sh', str(measure))
    modified = modified.replace('/var/run/opnsense-librespeed.lock', str(base/'measure.lock'))
    modified = modified.replace("LOCKF = '/usr/bin/lockf'", f"LOCKF = '{busy}'")
    runner.write_text(modified)
    outcome = subprocess.run([sys.executable, str(runner), 'start'], capture_output=True, text=True, timeout=5)
    response = json.loads(outcome.stdout)
    assert response['status'] == 'error' and 'Cron' in response['message'], response
    print('Cron overlap rejected OK')

api = (ROOT/'src/HistoryController.php').read_text()
acl = (ROOT/'src/ACL.xml').read_text()
ui = (ROOT/'src/csvspeedtest_report.js').read_text()
view = (ROOT/'src/index.volt').read_text()
actions = (ROOT/'src/actions_csvspeedtest.conf').read_text()
assert 'manualstartAction' in api and 'manualstatusAction' in api
assert 'throwNotFullAdmin()' in api.split('function manualstartAction',1)[1].split('function manualstatusAction',1)[0]
assert '<pattern>api/csvspeedtest/history/manualstart</pattern>' in acl
assert '[manual_start]' in actions and '[manual_status]' in actions
assert 'id="st-manual-start"' in view and 'id="st-manual-message"' in view
assert 'ajaxCall(`${API}/manualstart`' in ui and 'manualstatus' in ui
assert "fetchTable(); fetchCharts();" in ui
print('manual UI/API authorization checks OK')
