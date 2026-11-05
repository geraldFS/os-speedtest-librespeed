#!/bin/sh
# Only remove an exactly marked package-owned GUI job, never user's schedule.
if [ -x /usr/local/opnsense/speedtest-csv-dashboard/configure-cron.sh ]; then
    sh /usr/local/opnsense/speedtest-csv-dashboard/configure-cron.sh --remove-owned || \
        echo 'WARNUNG: Cron-Bereinigung fehlgeschlagen; bitte GUI-Cron pruefen.' >&2
fi
