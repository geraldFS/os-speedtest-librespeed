#!/usr/local/bin/python3
"""Read LibreSpeed's public server list on demand; return bounded structured JSON."""
import json
import re
import subprocess
import sys

CLI = '/usr/local/bin/librespeed-cli'
ENTRY = re.compile(r'^\s*([1-9][0-9]{0,9}):\s+(.+?)\s+\((https?://[^\s)]+)\)', re.I)
CONTROL = re.compile(r'[\x00-\x1f\x7f-\x9f]')

def parse(text):
    servers, seen = [], set()
    for line in text.splitlines():
        line = CONTROL.sub('', line)
        m = ENTRY.match(line)
        if not m: continue
        sid = int(m.group(1))
        if sid > 2147483647 or sid in seen: continue
        seen.add(sid)
        servers.append({'id':sid,'name':m.group(2).strip()[:200], 'url':m.group(3)[:500]})
        if len(servers) >= 200: break
    return sorted(servers, key=lambda x: (x['name'].casefold(),x['id']))

def run():
    try:
        proc = subprocess.run([CLI,'--list'], capture_output=True, text=True, timeout=35)
        if proc.returncode:
            raise ValueError('LibreSpeed list failed; retry later')
        if len(proc.stdout) > 100000:
            raise ValueError('server list too large')
        rows = parse(proc.stdout)
        if not rows: raise ValueError('no server entries in CLI output')
        return {'servers': rows, 'error': None}
    except Exception as e:
        return {'servers': [], 'error': str(e)[:160]}

if __name__ == '__main__':
    print(json.dumps(run(), ensure_ascii=False))
