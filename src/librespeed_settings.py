#!/usr/local/bin/python3
"""Validated persistent LibreSpeed CLI settings, never executable shell text."""
import json
import os
from pathlib import Path
import tempfile

CONFIG = Path('/usr/local/etc/os-speedtest/server-settings.json')
DEFAULT = {'mode': 'auto', 'servers': [], 'execution': 'sequential', 'concurrent': 6, 'duration': 20}

def validate(data):
    if not isinstance(data, dict):
        raise ValueError('settings must be an object')
    mode = data.get('mode', 'auto')
    execution = data.get('execution', 'sequential')
    if mode not in ('auto', 'selected') or execution not in ('sequential', 'parallel'):
        raise ValueError('invalid measurement mode')
    ids = data.get('servers', [])
    if not isinstance(ids, list) or len(ids) > 3:
        raise ValueError('select up to three server IDs')
    parsed = []
    for sid in ids:
        if isinstance(sid, bool) or not isinstance(sid, (int, str)):
            raise ValueError('invalid server ID type')
        if isinstance(sid, str) and (not sid.isascii() or not sid.isdecimal()):
            raise ValueError('server IDs must be positive integers')
        n = int(sid)
        if n < 1 or n > 2147483647 or n in parsed:
            raise ValueError('invalid or repeated server ID')
        parsed.append(n)
    if mode == 'selected' and not parsed:
        raise ValueError('choose at least one server for fixed mode')
    result = {'mode': mode, 'servers': parsed, 'execution': execution}
    for key, lower, upper in [('concurrent',1,12), ('duration',5,60)]:
        val = data.get(key, DEFAULT[key])
        if isinstance(val, bool) or not isinstance(val, (int, str)) or (isinstance(val, str) and not val.isdecimal()):
            raise ValueError('invalid ' + key)
        val = int(val)
        if not lower <= val <= upper:
            raise ValueError(key + ' outside allowed range')
        result[key] = val
    return result

def read_settings(path=CONFIG):
    path = Path(path)
    if path.is_symlink():
        raise ValueError('settings path is symlink')
    if not path.exists():
        return dict(DEFAULT)
    if not path.is_file() or path.stat().st_size > 4096:
        raise ValueError('invalid settings file')
    with path.open('r', encoding='utf-8') as f:
        return validate(json.load(f))

def save_settings(data, path=CONFIG):
    result = validate(data)
    path = Path(path)
    if path.is_symlink():
        raise ValueError('settings path is symlink')
    parent = path.parent
    parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    os.chmod(parent, 0o700)
    fd, tmp = tempfile.mkstemp(prefix='.server-settings-', suffix='.tmp', dir=str(parent))
    try:
        os.fchmod(fd, 0o600)
        with os.fdopen(fd, 'w', encoding='utf-8') as f:
            json.dump(result, f, separators=(',', ':'), sort_keys=True)
            f.write('\n')
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, path)
        dfd = os.open(parent, os.O_RDONLY)
        try: os.fsync(dfd)
        finally: os.close(dfd)
    finally:
        if os.path.exists(tmp): os.unlink(tmp)
    return result
