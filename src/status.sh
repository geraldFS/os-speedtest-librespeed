#!/bin/sh
set -eu
echo 'LibreSpeed Reporting v0.5.4-L (community package)'
opnsense-version || true
for item in /usr/local/opnsense/mvc/app/controllers/OPNsense/Csvspeedtest/Api/HistoryController.php \
 /usr/local/opnsense/mvc/app/models/OPNsense/Csvspeedtest/Menu/Menu.xml \
 /usr/local/opnsense/www/js/widgets/SpeedtestCsv.js \
 /usr/local/opnsense/scripts/csvspeedtest/measure.sh \
 /usr/local/opnsense/scripts/csvspeedtest/info.py \
 /usr/local/opnsense/scripts/csvspeedtest/manual_run.py; do
    if [ -f "$item" ]; then echo "OK      $item"; else echo "FEHLT   $item"; fi
done
if [ -x /usr/local/bin/librespeed-cli ]; then
 /usr/local/bin/librespeed-cli --version || true
 sha256 /usr/local/bin/librespeed-cli || true
else echo 'FEHLT: LibreSpeed CLI'; fi
pkg info os-speedtest-csv-reporting 2>/dev/null | head -n 3 || true
for item in /var/log/librespeed.csv /var/log/librespeed_provenance.csv; do
 [ ! -e "$item" ] || ls -lh "$item"
done
if [ -x /usr/local/opnsense/speedtest-csv-dashboard/configure-cron.sh ]; then
 sh /usr/local/opnsense/speedtest-csv-dashboard/configure-cron.sh --status || true
fi
