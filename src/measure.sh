#!/bin/sh
# LibreSpeed ONLY. Python used for JSON/CSV logging, NOT as a speedtest engine.
set -eu
umask 077
SELF=/usr/local/opnsense/scripts/csvspeedtest/measure.sh
LOCK=/var/run/opnsense-librespeed.lock
if [ "${1:-}" != '--locked' ]; then
    exec /usr/bin/lockf -t 0 "$LOCK" "$SELF" --locked
fi
exec /usr/local/bin/python3 /usr/local/opnsense/scripts/csvspeedtest/measure_libre.py
