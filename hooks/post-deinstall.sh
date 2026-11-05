#!/bin/sh
# No deletion of /var/log/librespeed*.csv, vendor LibreSpeed CLI, user's Cron entries.
LEGACY=/usr/local/etc/cron.d/opnsense-speedtest-reporting
if [ -f "$LEGACY" ] && grep -qF '# Managed by os-speedtest-csv-reporting' "$LEGACY"; then
    rm -f "$LEGACY"
fi
rm -f /tmp/opnsense_menu_cache.xml /tmp/opnsense_acl_cache.json \
      /var/lib/php/tmp/opnsense_menu_cache.xml /var/lib/php/tmp/opnsense_acl_cache.json
service configd restart >/dev/null 2>&1 || true
printf '%s\n' 'Mess-CSV, Versionsnachweise, LibreSpeed CLI und fremde GUI-Cronjobs beibehalten.'
