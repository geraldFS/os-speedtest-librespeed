#!/usr/bin/env python3
"""Offline regression tests for LibreSpeed CLI 1.0.14 JSON output.

No bandwidth requests and no writes outside TemporaryDirectory().
"""
import csv
import importlib.util
import json
import os
from pathlib import Path
import subprocess
from tempfile import TemporaryDirectory
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
import sys
sys.path.insert(0, str(ROOT/'src'))
spec = importlib.util.spec_from_file_location('measure_libre', ROOT/'src/measure_libre.py')
libre = importlib.util.module_from_spec(spec)
spec.loader.exec_module(libre)

SAMPLE = {
    'timestamp': '2026-11-05T20:30:00+01:00',
    'server': {'name':'Demo LibreSpeed', 'url':'https://example.invalid/speedtest/'},
    'client': {'ip':'192.0.2.1'},
    'bytes_sent':123, 'bytes_received':456,
    'download':323.19, 'upload':216.49, 'ping':13.78, 'jitter':0.17,
    'share':''
}

with TemporaryDirectory() as td:
    root=Path(td)
    binary=root/'librespeed-cli'
    binary.write_bytes(b'MOCK CLI; NO NETWORK REQUESTS')
    binary.chmod(0o700)
    libre.BIN=binary
    libre.LOG=root/'librespeed.csv'
    libre.PROV=root/'librespeed_provenance.csv'
    libre.ERR=root/'librespeed-error.log'
    outgoing = [SAMPLE]
    def mock_run(cmd, **kwargs):
        if cmd==[str(binary),'--version']:
            return subprocess.CompletedProcess(cmd,0,stdout='librespeed-cli v1.0.14\nLicense: LGPL-3.0\n',stderr='')
        if cmd==[str(binary),'--json','--concurrent','6','--duration','20']:
            return subprocess.CompletedProcess(cmd,0,stdout=json.dumps(outgoing),stderr='')
        if cmd==['/usr/local/sbin/opnsense-version']:
            return subprocess.CompletedProcess(cmd,0,stdout='OPNsense 26.7.8_2\n',stderr='')
        raise AssertionError(f'unexpected command {cmd!r}')
    with patch.object(libre.subprocess, 'run', side_effect=mock_run), \
         patch.object(libre, 'read_settings', return_value={'mode':'auto','servers':[],'execution':'sequential','concurrent':6,'duration':20}):
        # Official v1.0.14: --json returns an array, even when one server was tested.
        libre.run()
        with libre.LOG.open(newline='') as fp: data=list(csv.reader(fp))
        assert data[0]==libre.HEADER
        assert len(data)==2, data
        assert data[1][1:7]==['Demo LibreSpeed','https://example.invalid/speedtest/','323.19','216.49','13.78','0.17'],data
        assert data[1][7]=='librespeed-cli v1.0.14',data
        with libre.PROV.open(newline='') as fp: sidecar=list(csv.reader(fp))
        assert len(sidecar)==2,sidecar
        assert sidecar[1][0]==data[1][0]
        assert sidecar[1][1]==data[1][7]
        assert len(sidecar[1][2])==64

        # Optional multi-server: log all reports once, preserving separate server details.
        outgoing=[SAMPLE,{**SAMPLE,'server':{'name':'Another server','url':'https://example.net/'},'download':200.5}]
        libre.run()
        with libre.LOG.open(newline='') as fp: multi=list(csv.reader(fp))
        assert len(multi)==4,multi
        assert multi[-1][1]=='Another server' and multi[-1][3]=='200.5',multi
        with libre.PROV.open(newline='') as fp: multi_p=list(csv.reader(fp))
        assert len(multi_p)==4

        # An empty array indicates no usable server results; do not write fake measurements.
        outgoing=[]
        try: libre.run()
        except ValueError as exc: assert 'no measurements' in str(exc)
        else: raise AssertionError('Empty array was accepted')
        with libre.LOG.open(newline='') as fp: assert len(list(csv.reader(fp)))==4

        # If any server result is malformed, reject the whole run before writing.
        outgoing=[SAMPLE,{**SAMPLE,'jitter':'not-numeric'}]
        try: libre.run()
        except ValueError: pass
        else: raise AssertionError('Invalid jitter was accepted')
        with libre.LOG.open(newline='') as fp: assert len(list(csv.reader(fp)))==4

        # Compatibility: accept single-object CLI forks too.
        outgoing=SAMPLE
        libre.run()
        with libre.LOG.open(newline='') as fp: assert len(list(csv.reader(fp)))==5

print('LibreSpeed CLI JSON array, multi-server, empty, invalid and object tests passed')
