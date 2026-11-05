#!/usr/bin/env python3
"""Reproducible FreeBSD .pkg archive creator for developer/release builders.

The LGPL-3.0 LibreSpeed CLI binary is not bundled; the installer fetches it separately.
Installation on OPNsense must be validated by pkg before public distribution.
This build-time Python script is NOT Python's speedtest-cli measurement program.
"""
from pathlib import Path
import hashlib
import io
import json
import subprocess
import tarfile

ROOT = Path(__file__).resolve().parent
NAME = 'os-speedtest-csv-reporting'
VERSION = '0.5.4-L'
OUT = ROOT / 'dist' / f'{NAME}-{VERSION}.pkg'
FILES = {}
for line in (ROOT / 'manifest.txt').read_text().splitlines():
    if line.strip():
        src, dest = line.split('|', 1)
        f = ROOT / src
        assert dest.startswith('/usr/local/opnsense/') and f.is_file()
        FILES[dest] = f
SCRIPTS = {
    'pre-install': (ROOT / 'hooks/pre-install.sh').read_text(),
    'post-install': (ROOT / 'hooks/post-install.sh').read_text(),
    'pre-deinstall': (ROOT / 'hooks/pre-deinstall.sh').read_text(),
    'post-deinstall': (ROOT / 'hooks/post-deinstall.sh').read_text(),
}
M = {
    'name': NAME,
    'origin': 'local/os-speedtest-csv-reporting',
    'version': VERSION,
    'comment': 'Unofficial LibreSpeed reporting for OPNsense 26.7',
    'maintainer': 'geraldFS',
    'www': 'https://github.com/geraldFS/os-speedtest-librespeed',
    'arch': 'FreeBSD:15:amd64',
    'abi': 'FreeBSD:15:amd64',
    'prefix': '/usr/local',
    'licenselogic': 'single',
    'licenses': ['MIT'],
    'desc': ('Unofficial OPNsense CSV reporting plugin. Dashboard, table, vendor CLI '
             'identity, version evidence CSV, logs and hourly cron integration. '
             'Requires LibreSpeed CLI, never the Python speedtest-cli. '
             'Does not bundle LibreSpeed CLI or user measurement data.'),
    'flatsize': sum(f.stat().st_size for f in FILES.values()),
    # CLI is installed by +PRE_INSTALL if missing. It may otherwise be installed
    # directly from the vendor and need not be registered under the
    # FreeBSD Ports package name librespeed-cli. The bundle installer
    # bootstraps the official CLI before calling pkg add.
    'scripts': SCRIPTS,
    'files': {dest: '1$' + hashlib.sha256(f.read_bytes()).hexdigest() for dest, f in FILES.items()},
}
COMPACT = {k: v for k, v in M.items() if k not in ('files', 'scripts')}

def add(tar, path, data, mode):
    b = data if isinstance(data, bytes) else data.encode()
    hdr = tarfile.TarInfo(path)
    hdr.mode = mode
    hdr.uid = hdr.gid = 0
    hdr.uname, hdr.gname = 'root', 'wheel'
    hdr.mtime = 1793790000
    hdr.size = len(b)
    tar.addfile(hdr, io.BytesIO(b))

OUT.parent.mkdir(exist_ok=True)
raw = ROOT / 'dist/build.tar'
with tarfile.open(raw, 'w', format=tarfile.PAX_FORMAT) as tar:
    add(tar, '+COMPACT_MANIFEST', json.dumps(COMPACT, separators=(',', ':')) + '\n', 0o644)
    add(tar, '+MANIFEST', json.dumps(M, separators=(',', ':')) + '\n', 0o644)
    for step, script in SCRIPTS.items():
        add(tar, {'pre-install': '+PRE_INSTALL',
                  'post-install': '+POST_INSTALL',
                  'pre-deinstall': '+PRE_DEINSTALL',
                  'post-deinstall': '+POST_DEINSTALL'}[step], script, 0o755)
    for dest, f in sorted(FILES.items()):
        mode = 0o755 if dest.endswith(('.sh', '.py')) else 0o644
        # IMPORTANT: preserve the leading / exactly as in +MANIFEST.
        # pkg_absolutepath() otherwise produces //usr/local/... at extraction
        # and pkg fails to find the resulting path in its manifest.
        add(tar, dest, f.read_bytes(), mode)
subprocess.run(['zstd', '-q', '-f', '-15', '-o', str(OUT), str(raw)], check=True)
raw.unlink()
print(f'{OUT.name}\t{OUT.stat().st_size} bytes')
print('SHA256:', hashlib.sha256(OUT.read_bytes()).hexdigest())
