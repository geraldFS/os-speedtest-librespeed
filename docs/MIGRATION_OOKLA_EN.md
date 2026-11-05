# Migration: remove older Ookla and os-speedtest versions, install LibreSpeed

**For:** OPNsense 26.7.x / amd64, os-speedtest **0.5.4-L**. The previous `os-speedtest-csv-reporting` package and the Ookla executable `/usr/local/bin/speedtest` are **different components** and must be assessed separately.

**First:** Back up the OPNsense configuration and preserve old CSV logs. Run commands as `root` over SSH/console.

## 1. Check what is installed, and back up old measurements

```sh
opnsense-version
pkg info os-speedtest-csv-reporting || true
pkg which /usr/local/bin/speedtest
/usr/local/bin/librespeed-cli --version 2>/dev/null || true
ls -lh /var/log/speedtest*.csv /var/log/librespeed*.csv 2>/dev/null
mkdir -p /root/speedtest-migration-backup
for f in /var/log/speedtest.csv /var/log/speedtest_provenance.csv /var/log/librespeed.csv /var/log/librespeed_provenance.csv; do
  [ ! -f "$f" ] || cp -p "$f" /root/speedtest-migration-backup/
done
```

Copy the backups off the firewall for independent retention.

## 2. Disable old Ookla jobs

Under **System → Settings → Cron**, disable old Ookla commands such as `speedtest_cron.sh`. Inspect remaining scheduled entries:

```sh
grep -RniE 'ookla|speedtest_cron|csvspeedtest|librespeed' \
  /etc/crontab /usr/local/etc/cron.d /var/cron/tabs 2>/dev/null || true
```

Do not delete matching files without identifying who owns them. The new manual measurement button does not modify Cron.

## 3. Remove only the old Ookla plugin (0.4.x)

```sh
pkg query '%n %v' os-speedtest-csv-reporting 2>/dev/null || true
```

If 0.4.x is installed, back up the configuration, then run `pkg delete os-speedtest-csv-reporting`. If 0.5.0-L through 0.5.3-L is installed, **do not uninstall**: the full installer upgrades it directly. If there is no installed package, skip this step. Measurement data is not part of the package payload, but retain your independent backup.

## 4. Remove the Ookla executable separately

Run `pkg which /usr/local/bin/speedtest`. If a registered package owns the executable, identify that exact package, review its dependencies and other uses, and then delete **only** the corresponding Ookla package if appropriate. Do not guess a package name.

If the file is not package-managed, disable it first (reversible):

```sh
if [ -f /usr/local/bin/speedtest ] && [ ! -L /usr/local/bin/speedtest ]; then
  mv /usr/local/bin/speedtest /usr/local/bin/speedtest.ookla-disabled
fi
```

After LibreSpeed is verified, optionally remove the saved executable using `rm -i /usr/local/bin/speedtest.ookla-disabled`. Remove legacy custom `speedtest_cron.sh` and `actions_speedtest.conf` **only** after checking that no job or application uses them.

The new plugin deliberately does not delete Ookla binaries on its own.

## 5. Install the LibreSpeed all-in-one archive

Copy `os-speedtest_0.5.4-L.tar.gz` to `/tmp` and verify its accompanying SHA-256 checksum first:

```powershell
scp .\os-speedtest_0.5.4-L.tar.gz root@FIREWALL-IP:/tmp/
```

On the firewall:

```sh
cd /tmp
tar -xzf os-speedtest_0.5.4-L.tar.gz
cd os-speedtest_0.5.4-L
sh install.sh
```

The full installer installs/verifies the **official LibreSpeed CLI**. It never installs Python `speedtest-cli` or Ookla. The standalone `.pkg` requires LibreSpeed CLI to be present beforehand.

## 6. Manual measurement from the GUI

Under **Reporting → Speedtest**, refresh the server list, select up to three servers, choose **Selected servers** and **Sequential** for comparable results, select duration/concurrent HTTP requests, and press **Save settings**. Then press **Run measurement now**. The status is polled in the background; the historical table and charts refresh after completion. Unsaved settings do not apply to the current run. A manual test never changes the scheduled Cron job.

## 7. Verify and troubleshoot

```sh
pkg info os-speedtest-csv-reporting
/usr/local/bin/librespeed-cli --version
sh /usr/local/opnsense/speedtest-csv-dashboard/status.sh
tail -n 5 /var/log/librespeed.csv
tail -n 20 /var/log/librespeed-error.log
```

Check **System → Settings → Cron** for duplicate jobs. If no measurement has succeeded, `/var/log/librespeed.csv` may not exist yet.

## 8. Uninstall while retaining measurements

```sh
pkg delete os-speedtest-csv-reporting
```

Package hooks are designed to preserve historical CSV logs, the separately installed LibreSpeed CLI, and user-managed Cron jobs. Confirm behavior on your own OPNsense before publishing a stable release. Measurements are not official provider dispute certificates.
