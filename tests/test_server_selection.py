#!/usr/bin/env python3
"""Offline configd list parsing, validation, and measurement scheduling regressions."""
import csv
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'src'))
from librespeed_settings import DEFAULT, read_settings, save_settings, validate
from servers_list import parse

assert validate(DEFAULT) == DEFAULT
assert validate({'mode':'selected','servers':['50','79',105], 'execution':'sequential','concurrent':6,'duration':20})['servers'] == [50,79,105]
for fail in [
    {'mode':'selected','servers':[]},
    {'mode':'selected','servers':[50,79,105,51]},
    {'mode':'selected','servers':[50,50]},
    {'mode':'selected','servers':['50;rm -rf /']},
    {'mode':'selected','servers':[50], 'concurrent':1000},
    {'mode':'selected','servers':[50], 'duration':0},
    {'mode':'evil','servers':[]},
]:
    try: validate(fail)
    except ValueError: pass
    else: raise AssertionError('invalid config accepted: ' + repr(fail))
with tempfile.TemporaryDirectory() as d:
    path = Path(d)/'private'/'settings.json'
    data = validate({'mode':'selected','servers':[50,79,105], 'execution':'parallel','concurrent':6,'duration':20})
    assert save_settings(data, path)==data
    assert read_settings(path)==data
    assert path.stat().st_mode & 0o777 == 0o600
    assert path.parent.stat().st_mode & 0o777 == 0o700

sample_list = '''Retrieving server list from https://librespeed.org/backend-servers/servers.php
51: Amsterdam, Netherlands (Clouvider) (https://ams.speedtest.clouvider.net/backend) [Sponsor: Clouvider]
50: Frankfurt, Germany (Clouvider) (https://fra.speedtest.clouvider.net/backend) [Sponsor: Clouvider]
79: Prague, Czech Republic (CESNET) (https://speedtest.cesnet.cz) [Sponsor: CESNET]
105: Frankfurt, Germany (FS IT-Systeme GmbH) (https://speed.fs-it.systems/) [Sponsor: FS IT]
'''
servers = parse(sample_list)
assert {s['id'] for s in servers} == {50,51,79,105}
assert next(s for s in servers if s['id']==50)['name']=='Frankfurt, Germany (Clouvider)'

spec = importlib.util.spec_from_file_location('measure', ROOT/'src/measure_libre.py')
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
SAMPLE = {'server': {'name':'Clouvider Frankfurt', 'url':'https://example.test'}, 'download':251.81,'upload':208.41,'ping':10.94,'jitter':0.08}
with tempfile.TemporaryDirectory() as td:
    d=Path(td)
    binary=d/'librespeed-cli';binary.write_bytes(b'MOCK');binary.chmod(0o700)
    mod.BIN=binary;mod.LOG=d/'librespeed.csv';mod.PROV=d/'librespeed_provenance.csv';mod.ERR=d/'error.log'
    calls=[]
    def fake_run(cmd, **kwargs):
        calls.append(cmd)
        if cmd==[str(binary),'--version']:
            return subprocess.CompletedProcess(cmd,0,stdout='librespeed-cli v1.0.14\n',stderr='')
        if cmd==['/usr/local/sbin/opnsense-version']:
            return subprocess.CompletedProcess(cmd,0,stdout='OPNsense 26.7.8_2\n',stderr='')
        if '--json' in cmd:
            sid = cmd[cmd.index('--server')+1] if '--server' in cmd else '50'
            # CLI's repeated server flags return separate measurement records.
            num = len([a for a in cmd if a=='--server']) or 1
            return subprocess.CompletedProcess(cmd,0,stdout=json.dumps([{**SAMPLE, 'server':{'name':f'Server {sid}-{i}','url':f'https://example.test/{i}'}} for i in range(num)]),stderr='')
        raise AssertionError(cmd)
    with patch.object(mod.subprocess,'run',side_effect=fake_run):
        with patch.object(mod, 'read_settings', return_value=validate({'mode':'selected','servers':[50,79,105],'execution':'sequential','concurrent':6,'duration':20})):
            mod.run()
        cmd = next(c for c in calls if '--json' in c)
        assert cmd.count('--server')==3 and cmd[-6:]==['--server','50','--server','79','--server','105'],cmd
        with mod.LOG.open(newline='') as f: assert len(list(csv.reader(f)))==4
        calls.clear()
        with patch.object(mod, 'read_settings', return_value=validate({'mode':'selected','servers':[50,79,105],'execution':'parallel','concurrent':6,'duration':20})):
            mod.run()
        cmds=[c for c in calls if '--json' in c]
        assert len(cmds)==3 and all(c.count('--server')==1 for c in cmds),cmds
        with mod.LOG.open(newline='') as f: assert len(list(csv.reader(f)))==7

print('Server list parsing, settings validation, sequential and parallel CLI modes: OK')
