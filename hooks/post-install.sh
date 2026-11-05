#!/bin/sh
# OPNsense package lifecycle; do not modify measurement CSV or LibreSpeed binary.
rm -f /tmp/opnsense_menu_cache.xml /tmp/opnsense_acl_cache.json \
      /var/lib/php/tmp/opnsense_menu_cache.xml /var/lib/php/tmp/opnsense_acl_cache.json
# Volt compiles MVC views into PHP files. Old compiled 0.4.x templates
# can survive a pkg upgrade and still display outdated headings/columns.
# Only remove cached pages belonging to this plugin, not global PHP cache.
if [ -d /var/lib/php/cache ]; then
    find /var/lib/php/cache -maxdepth 1 -type f -iname '*csvspeedtest*' -delete
fi
service configd restart >/dev/null 2>&1 || echo 'configd-Neustart erforderlich.' >&2
if [ -x /usr/local/opnsense/speedtest-csv-dashboard/configure-cron.sh ]; then
    sh /usr/local/opnsense/speedtest-csv-dashboard/configure-cron.sh --ensure || \
        echo 'ACHTUNG: GUI-Cron-Auftrag wurde nicht bestaetigt. Status und OPNsense Cron pruefen.' >&2
fi
printf '%s\n' 'LibreSpeed Reporting 0.5.4-L: LibreSpeed-Volt-Cache entfernt; WebGUI-Neustart nach Paketinstallation empfohlen.'
