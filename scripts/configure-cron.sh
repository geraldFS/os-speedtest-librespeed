#!/bin/sh
# Idempotent OPNsense GUI Cron management; no new hidden jobs.
set -eu
LEGACY=/usr/local/etc/cron.d/opnsense-speedtest-reporting
TAG='# Managed by os-speedtest-csv-reporting'
PHP=/usr/local/bin/php
MANAGER=/usr/local/opnsense/scripts/csvspeedtest/manage-cron.php
case "${1:---ensure}" in
    --ensure|--status|--remove-owned) ACTION=${1:---ensure} ;;
    --disable) ACTION=--remove-owned ;;
    *) echo 'Use: configure-cron.sh --ensure|--remove-owned|--status' >&2; exit 2 ;;
esac
[ -x "$PHP" ] && [ -f "$MANAGER" ] || {
    echo "OPNsense cron PHP components missing" >&2; exit 1;
}
# Avoid a duplicate when another unmanaged file explicitly schedules Speedtest.
if [ "$ACTION" = --ensure ]; then
    if grep -Eil 'speedtest_cron[.]sh|csvspeedtest/measure[.]sh|configctl .*csvspeedtest run|librespeed-cli' \
         /var/cron/tabs/* /usr/local/etc/cron.d/* 2>/dev/null | \
         grep -v -F -x "$LEGACY" >/dev/null 2>&1; then
        echo 'Cron: anderer Dateisystem-Cronjob gefunden; GUI-Auftrag NICHT automatisch angelegt.'
        exit 0
    fi
fi
"$PHP" "$MANAGER" "$ACTION"
# Drop our *old* hidden cron only after successfully handling the GUI job,
# never delete a file not marked as ours.
if [ "$ACTION" = --ensure ] || [ "$ACTION" = --remove-owned ]; then
    if [ -f "$LEGACY" ] && grep -qF "$TAG" "$LEGACY"; then
        rm -f "$LEGACY"
        echo 'Cron: alter versteckter Paketauftrag entfernt.'
    fi
    # On OPNsense cron restart renders config.xml GUI entries to cron.
    /usr/local/sbin/configctl cron restart || {
        echo 'HINWEIS: Cron konnte nicht neu geladen werden; GUI Apply ausfuehren.' >&2
        exit 1
    }
fi
