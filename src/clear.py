#!/usr/local/bin/python3
"""Privileged configd action: back up /var/log/librespeed.csv, truncate in place,
keep the header, and leave existing Cron configuration untouched.

No command-line or HTTP-provided paths accepted.
"""
import fcntl
import json
import os
import shutil
import stat
import sys
from datetime import datetime

CSV = '/var/log/librespeed.csv'
BACKUPS = '/usr/local/opnsense/speedtest-csv-dashboard/librespeed-cleared-logs'


def emit(status, message, backup=None):
    result = {'status': status, 'message': message}
    if backup is not None:
        result['backup'] = backup
    print(json.dumps(result, ensure_ascii=False), flush=True)


def clear():
    if os.geteuid() != 0:
        raise PermissionError('Nur als root ueber configd ausfuehren')
    flags = os.O_RDWR | getattr(os, 'O_NOFOLLOW', 0) | getattr(os, 'O_CLOEXEC', 0)
    fd = os.open(CSV, flags)
    try:
        if not stat.S_ISREG(os.fstat(fd).st_mode):
            raise ValueError('Logdatei ist keine regulaere Datei')
        fcntl.flock(fd, fcntl.LOCK_EX)
        with os.fdopen(os.dup(fd), 'r+b', buffering=0) as source:
            source.seek(0)
            first_line = source.readline(2048)
            if not first_line or not first_line.startswith(b'Timestamp,ServerName,ServerURL,') or b'\n' not in first_line:
                raise ValueError('CSV-Kopfzeile fehlt oder ist ungueltig; Datei nicht veraendert')
            # Keep the file's original header (legacy installs use seven columns).
            # Only normalized LibreSpeed CSV is accepted.
            os.makedirs(BACKUPS, mode=0o700, exist_ok=True)
            if os.path.islink(BACKUPS) or not stat.S_ISDIR(os.stat(BACKUPS).st_mode):
                raise ValueError('Sicherungsverzeichnis ist unsicher')
            os.chmod(BACKUPS, 0o700)
            total_size = os.fstat(fd).st_size
            free = shutil.disk_usage(BACKUPS).free
            if free < total_size + (1024 * 1024):
                raise OSError('Zu wenig freier Speicher fuer eine Sicherung')
            timestamp = datetime.now().strftime('%Y%m%d-%H%M%S-%f')
            filename = f'librespeed-before-clear-{timestamp}-{os.getpid()}.csv'
            backup = os.path.join(BACKUPS, filename)
            backup_fd = os.open(backup, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
            try:
                with os.fdopen(backup_fd, 'wb') as destination:
                    source.seek(0)
                    shutil.copyfileobj(source, destination, length=1024 * 1024)
                    destination.flush()
                    os.fsync(destination.fileno())
            except Exception:
                try:
                    os.unlink(backup)
                except OSError:
                    pass
                raise
            # Preserve inode, ownership and permissions for the existing Cron writer.
            os.lseek(fd, 0, os.SEEK_SET)
            os.ftruncate(fd, 0)
            os.write(fd, first_line)
            os.fsync(fd)
            emit('ok', 'Log geleert (Kopfzeile erhalten); Sicherung erstellt.', backup)
    finally:
        os.close(fd)


if __name__ == '__main__':
    try:
        clear()
    except Exception as exc:
        emit('error', str(exc))
        sys.exit(1)
