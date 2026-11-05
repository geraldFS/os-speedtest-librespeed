#!/usr/local/bin/python3
"""Report the currently installed Speedtest program, without running a speed test.
Note: this is NOT proof of the binary used for historic CSV rows.
Configd action takes no parameters, uses a fixed path and emits JSON only.
"""
import datetime
import hashlib
import json
import os
import stat
import subprocess

BINARY = '/usr/local/bin/librespeed-cli'


def cli_info():
    current = datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='seconds')
    result = {'installed': False, 'officialLibreSpeed': False, 'path': BINARY,
              'version': None, 'sha256': None, 'package': None,
              'checkedAt': current}
    if os.path.islink(BINARY) or not os.path.isfile(BINARY) or not os.access(BINARY, os.X_OK):
        return result
    file_info = os.stat(BINARY, follow_symlinks=False)
    if not stat.S_ISREG(file_info.st_mode):
        return result
    result['installed'] = True
    digest = hashlib.sha256()
    with open(BINARY, 'rb') as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b''):
            digest.update(block)
    result['sha256'] = digest.hexdigest()
    try:
        proc = subprocess.run([BINARY, '--version'], stdout=subprocess.PIPE,
                              stderr=subprocess.STDOUT, check=False, timeout=5,
                              text=True, errors='replace')
        raw = proc.stdout.strip()[:400]
        result['version'] = raw.splitlines()[0].strip() if proc.returncode == 0 and raw else None
        result['officialLibreSpeed'] = bool(raw and 'librespeed' in raw.lower() and proc.returncode == 0)
    except (OSError, subprocess.TimeoutExpired):
        pass
    try:
        pkg_binary = '/usr/local/sbin/pkg' if os.path.exists('/usr/local/sbin/pkg') else '/usr/sbin/pkg'
        proc = subprocess.run([pkg_binary, 'which', '-q', BINARY],
                              stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
                              check=False, timeout=4, text=True, errors='replace')
        if proc.returncode == 0 and proc.stdout.strip():
            result['package'] = proc.stdout.strip()[:200]
    except (OSError, subprocess.TimeoutExpired):
        pass
    return result


if __name__ == '__main__':
    try:
        print(json.dumps(cli_info(), ensure_ascii=False))
    except Exception as error:
        print(json.dumps({'installed': False, 'error': type(error).__name__,
                          'path': BINARY, 'version': None, 'sha256': None,
                          'package': None, 'officialLibreSpeed': False,
                          'checkedAt': None}))
