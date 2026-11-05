#!/usr/local/bin/python3
"""Trigger/read an OPNsense LibreSpeed one-shot test without blocking PHP.

Fixed configd entrypoints only (no client-supplied shell or CLI arguments).
The worker executes the SAME measurement script as Cron, which holds its own
exclusive lock. On failure the CLI error is also recorded in librespeed-error.log.
"""
import datetime as dt
import fcntl
import json
import os
from pathlib import Path
import secrets
import stat
import subprocess
import sys

LOCK = Path('/var/run/opnsense-librespeed-manual.lock')
STATE = Path('/var/run/opnsense-librespeed-manual.json')
MEASURE = Path('/usr/local/opnsense/scripts/csvspeedtest/measure.sh')
MEASURE_LOCK = Path('/var/run/opnsense-librespeed.lock')
LOCKF = '/usr/bin/lockf'
MAX_DURATION = 900  # 3 servers * (60s per phase + overhead), plus safeguards


def timestamp():
    return dt.datetime.now(dt.timezone.utc).isoformat(timespec='seconds')


def get_lock():
    flags = os.O_CREAT | os.O_RDWR | getattr(os, 'O_NOFOLLOW', 0)
    fd = os.open(str(LOCK), flags, 0o600)
    info = os.fstat(fd)
    if not stat.S_ISREG(info.st_mode) or info.st_uid != 0:
        os.close(fd)
        raise RuntimeError('unsafe manual lock')
    fcntl.flock(fd, fcntl.LOCK_EX)
    return fd


def check_status_file():
    if STATE.is_symlink():
        raise RuntimeError('unsafe state symlink')
    if STATE.exists():
        info = STATE.stat()
        if not stat.S_ISREG(info.st_mode) or info.st_uid != 0 or info.st_size > 8192:
            raise RuntimeError('unsafe manual state')


def read_state():
    check_status_file()
    if not STATE.exists():
        return {'status': 'idle', 'message': 'Noch keine manuelle Messung gestartet'}
    data = json.loads(STATE.read_text(encoding='utf-8'))
    if not isinstance(data, dict) or 'status' not in data:
        raise RuntimeError('invalid manual status')
    return data


def write_status(data):
    check_status_file()
    name = str(STATE) + '.tmp.' + secrets.token_hex(8)
    fd = os.open(name, os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, 'O_NOFOLLOW', 0), 0o600)
    try:
        blob = (json.dumps(data, ensure_ascii=False, separators=(',', ':')) + '\n').encode('utf-8')
        os.write(fd, blob)
        os.fsync(fd)
    finally:
        os.close(fd)
    try:
        os.replace(name, STATE)
    finally:
        if os.path.exists(name):
            os.unlink(name)


def process_alive(pid):
    try:
        pid = int(pid)
        if pid < 2:
            return False
        os.kill(pid, 0)
        return True
    except (ValueError, TypeError, ProcessLookupError):
        return False
    except PermissionError:
        return True


def latest_state():
    obj = read_state()
    if obj['status'] in ('starting', 'running') and not process_alive(obj.get('pid')):
        obj['status'] = 'failed'
        obj['finished'] = timestamp()
        obj['message'] = 'Messprozess wurde beendet; Fehlerprotokoll prüfen'
        write_status(obj)
    return obj


def measurement_busy():
    # lockf -t 0 returns nonzero if an existing cron/manual measurement owns the lock.
    if not os.path.isfile(LOCKF):
        # In production measure.sh requires /usr/bin/lockf; its absence means
        # that we cannot safely coordinate a manual run with Cron.
        raise RuntimeError('lockf is missing')
    test = subprocess.run([LOCKF, '-t', '0', str(MEASURE_LOCK), '/usr/bin/true'],
                          stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=3)
    return test.returncode != 0


def start():
    fd = get_lock()
    try:
        state = latest_state()
        if state['status'] in ('starting', 'running'):
            return {'status': 'running', 'message': 'Es läuft bereits eine manuelle Messung',
                    'token': state.get('token')}
        if not MEASURE.is_file() or not os.access(MEASURE, os.X_OK):
            return {'status': 'error', 'message': 'LibreSpeed-Messskript fehlt'}
        if measurement_busy():
            return {'status': 'error', 'message': 'Ein Cron- oder anderer Messlauf ist bereits aktiv'}
        token = secrets.token_hex(12)
        try:
            child = subprocess.Popen([sys.executable, str(Path(__file__).resolve()), 'worker', token],
                                     stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
                                     stderr=subprocess.DEVNULL, cwd='/', start_new_session=True,
                                     close_fds=True)
        except OSError:
            return {'status': 'error', 'message': 'Messprozess konnte nicht gestartet werden'}
        write_status({'status': 'starting', 'pid': child.pid, 'token': token,
                      'started': timestamp(), 'message': 'Messung gestartet'})
        return {'status': 'starting', 'token': token, 'message': 'Messung gestartet'}
    finally:
        fcntl.flock(fd, fcntl.LOCK_UN)
        os.close(fd)


def worker(token):
    # The frontend's manual-start handler creates the token and starts us.
    fd = get_lock()
    try:
        state = read_state()
        if state.get('token') != token or state.get('pid') != os.getpid():
            return 2
        state['status'] = 'running'
        state['message'] = 'LibreSpeed misst die konfigurierten Server'
        write_status(state)
    finally:
        fcntl.flock(fd, fcntl.LOCK_UN)
        os.close(fd)
    success = False
    message = 'Unbekannter LibreSpeed-Fehler'
    try:
        outcome = subprocess.run([str(MEASURE)], capture_output=True, text=True, timeout=MAX_DURATION)
        success = outcome.returncode == 0
        message = 'Messung gespeichert' if success else 'Messung fehlgeschlagen; /var/log/librespeed-error.log prüfen'
    except subprocess.TimeoutExpired:
        message = 'Messung hat das maximale Zeitlimit überschritten'
    except OSError:
        message = 'Messskript konnte nicht gestartet werden'
    finally:
        fd = get_lock()
        try:
            state = read_state()
            if state.get('token') == token:
                state['status'] = 'done' if success else 'failed'
                state['finished'] = timestamp()
                state['message'] = message
                write_status(state)
        finally:
            fcntl.flock(fd, fcntl.LOCK_UN)
            os.close(fd)
    return 0 if success else 1


def status():
    fd = get_lock()
    try:
        data = latest_state()
        # Do not expose server command-line, local filesystem internals or PIDs.
        return {key: data[key] for key in ('status', 'message', 'started', 'finished', 'token') if key in data}
    finally:
        fcntl.flock(fd, fcntl.LOCK_UN)
        os.close(fd)


def main():
    action = sys.argv[1] if len(sys.argv) == 2 else ''
    if action == 'start' and len(sys.argv) == 2:
        print(json.dumps(start(), ensure_ascii=False))
    elif action == 'status' and len(sys.argv) == 2:
        print(json.dumps(status(), ensure_ascii=False))
    elif len(sys.argv) == 3 and sys.argv[1] == 'worker':
        return worker(sys.argv[2])
    else:
        print(json.dumps({'status': 'error', 'message': 'Unbekannte Aktion'}))
        return 1
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except Exception:
        if sys.argv[1:2] != ['worker']:
            print(json.dumps({'status': 'error', 'message': 'Messdienstfehler'}))
        sys.exit(1)
