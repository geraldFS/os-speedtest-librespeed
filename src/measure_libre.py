#!/usr/local/bin/python3
"""Invoke the LibreSpeed Go CLI, serialize its JSON report into independent CSV.
No Ookla, no Python speedtest package. Speeds in CLI JSON are already Mbps.
"""
import csv
import datetime as dt
import hashlib
import json
import os
import pathlib
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from librespeed_settings import read_settings

BIN = pathlib.Path('/usr/local/bin/librespeed-cli')
LOG = pathlib.Path('/var/log/librespeed.csv')
PROV = pathlib.Path('/var/log/librespeed_provenance.csv')
ERR = pathlib.Path('/var/log/librespeed-error.log')
HEADER = ['Timestamp','ServerName','ServerURL','Download_Mbps','Upload_Mbps','Ping_ms','Jitter_ms','CLI_Version']
PHEADER = ['Timestamp','LibreSpeedCLI','CLI_SHA256','OPNsenseVersion','ServerName','ServerURL']

def append_csv(path, header, record):
    if path.is_symlink() or (path.exists() and not path.is_file()):
        raise ValueError(f'unsafe log path: {path}')
    if path.exists() and path.stat().st_size:
        with path.open('r', newline='', encoding='utf-8') as fp:
            if next(csv.reader(fp), []) != header:
                raise ValueError(f'CSV header mismatch: {path}')
    with path.open('a', newline='', encoding='utf-8') as fp:
        writer=csv.writer(fp)
        if fp.tell()==0: writer.writerow(header)
        writer.writerow(record)
        fp.flush()
        os.fsync(fp.fileno())

def positive(value):
    if isinstance(value,bool) or not isinstance(value,(int,float)) or value<0 or value!=value or value==float('inf'):
        raise ValueError('non-finite / invalid speed or latency')
    return round(float(value), 5)

def run():
    if BIN.is_symlink() or not BIN.is_file() or not os.access(BIN,os.X_OK):
        raise ValueError('LibreSpeed CLI missing')
    ver_output=subprocess.run([str(BIN),'--version'],capture_output=True,text=True,timeout=8,check=True).stdout
    # Vendor --version prints multiple lines. Store one stable version line per CSV record.
    ver=next((line.strip() for line in ver_output.splitlines() if line.strip()), '')[:250]
    if not ver: raise ValueError('Empty LibreSpeed version')
    digest=hashlib.sha256(BIN.read_bytes()).hexdigest()
    cfg = read_settings()
    common = [str(BIN), '--json', '--concurrent', str(cfg['concurrent']), '--duration', str(cfg['duration'])]
    ids = cfg['servers'] if cfg['mode'] == 'selected' else []
    # --server repeated runs server tests in sequence. For parallel mode we
    # deliberately start distinct CLI processes; their reported rates contend
    # for the same physical link and must NOT be used as independent maxima.
    commands = []
    if cfg['mode'] == 'selected' and cfg['execution'] == 'parallel' and len(ids) > 1:
        commands = [common + ['--server', str(sid)] for sid in ids]
    else:
        commands = [common + [flag for sid in ids for flag in ('--server', str(sid))]]
    timeout = max(180, (cfg['duration'] * 2 + 45) * (len(ids) if len(commands) == 1 else 1))
    def cli_run(command):
        proc = subprocess.run(command, capture_output=True, text=True, timeout=timeout)
        if proc.returncode:
            raise RuntimeError('LibreSpeed CLI failed: '+proc.stderr[:500])
        return json.loads(proc.stdout)
    if len(commands) == 1:
        outputs = [cli_run(commands[0])]
    else:
        with ThreadPoolExecutor(max_workers=min(3, len(commands))) as pool:
            outputs = list(pool.map(cli_run, commands))
    # Normalize a separate array per process into one list for CSV logging.
    reports = []
    for output in outputs:
        if isinstance(output, dict):
            reports.append(output)
        elif isinstance(output, list) and output:
            reports.extend(output)
        else:
            raise ValueError('LibreSpeed JSON has no measurements (expected nonempty array)')
    records=[]
    for item in reports:
        if not isinstance(item, dict):
            raise ValueError('Invalid LibreSpeed JSON report entry')
        server=item.get('server') or {}
        if not isinstance(server, dict):
            raise ValueError('Invalid server')
        name=str(server.get('name') or '')[:200]
        url=str(server.get('url') or '')[:500]
        if not name and not url:
            raise ValueError('Missing LibreSpeed server identity')
        values=[positive(item[k]) for k in ('download','upload','ping','jitter')]
        records.append((name,url,values))
    stamp=dt.datetime.now().astimezone().strftime('%Y-%m-%d %H:%M:%S')
    osver=subprocess.run(['/usr/local/sbin/opnsense-version'],capture_output=True,text=True,timeout=5).stdout.strip()[:150]
    # Validate every response entry before writing the first row.
    for name,url,values in records:
        append_csv(LOG,HEADER,[stamp,name,url,*values,ver])
        append_csv(PROV,PHEADER,[stamp,ver,digest,osver,name,url])
        print(f'LibreSpeed result stored: {stamp} | {name} | {values[0]} Mbps down | {values[1]} Mbps up')

if __name__ == '__main__':
    try: run()
    except Exception as exc:
        # Only exception type and text; no secret raw JSON is persisted.
        with ERR.open('a',encoding='utf-8') as fp:
            fp.write(f'{dt.datetime.now().isoformat()} {type(exc).__name__}: {str(exc)[:500]}\n')
        print(f'LibreSpeed measurement failed: {exc}',file=sys.stderr)
        sys.exit(1)
