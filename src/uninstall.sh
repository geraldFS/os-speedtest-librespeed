#!/bin/sh
# Package-aware removal: never delete CSV files or LibreSpeed CLI.
set -eu
[ "$(id -u)" -eq 0 ] || { echo 'root erforderlich' >&2; exit 1; }
if pkg info -q os-speedtest-csv-reporting >/dev/null 2>&1; then
    pkg delete os-speedtest-csv-reporting
else
    echo 'Keine pkg-Installation erkannt. Bestehende manuelle Dateien bleiben unveraendert.' >&2
    exit 1
fi
