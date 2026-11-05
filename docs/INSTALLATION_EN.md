# Installation – os-speedtest 0.5.4-L (English)

**Target:** OPNsense 26.7.x, amd64. **Engine:** LibreSpeed CLI 1.0.14 only (LGPL-3.0). This version fixes the JSON array parsing bug in 0.5.0-L.

## Requirements

- Back up the firewall configuration, disable any old Ookla jobs, and obtain root console or SSH access.
- Internet access to the official LibreSpeed GitHub release if CLI is absent.
- Verify the release archive checksum before running any privileged installer.

## All-in-one installation (also upgrading from 0.5.0-L)

Transfer the archive to `/tmp` with SCP, then on OPNsense:

```sh
cd /tmp
tar -xzf os-speedtest_0.5.4-L.tar.gz
cd os-speedtest_0.5.4-L
sh install.sh
```

**Do not uninstall 0.5.0-L before upgrading.** The FreeBSD package name remains `os-speedtest-csv-reporting`.

## Test

```sh
pkg info os-speedtest-csv-reporting
/usr/local/bin/librespeed-cli --version
configctl csvspeedtest run
tail -n 5 /var/log/librespeed.csv
tail -n 10 /var/log/librespeed-error.log
```

The `configctl` command performs a real bandwidth test and may saturate the link temporarily; do not trigger repeatedly. The CSV file is created after the first successful measurement.

Check **Reporting → Speedtest**, **Lobby → Dashboard**, and **System → Settings → Cron** (only one active LibreSpeed task).

If the GUI still says the CSV is missing, inspect `/var/log/librespeed-error.log`, confirm CSV file permissions, and investigate CLI/network/server errors before running another test.

## Uninstall

```sh
pkg delete os-speedtest-csv-reporting
```

Existing log files, LibreSpeed CLI, and user-created Cron jobs should remain. Back up OPNsense configuration before performing changes.

## If outdated Ookla labels remain on the report page

Version 0.5.4-L clears the compiled LibreSpeed view and the full installer restarts WebGUI. If installing the `.pkg` directly, run:

```sh
find /var/lib/php/cache -maxdepth 1 -type f -iname '*csvspeedtest*' -print
find /var/lib/php/cache -maxdepth 1 -type f -iname '*csvspeedtest*' -delete
configctl webgui restart
```

Log in again and hard-reload the browser. No measurement CSV or Cron entries are removed.

### LibreSpeed server selection (0.5.4-L)

Use **Reporting → Speedtest**, refresh the `--list` server table, select up to three servers, choose sequential (recommended for independent speed tests) or simultaneous (bandwidth contention test), and save. Settings apply to both manual and cron runs. Configuration persists at `/usr/local/etc/os-speedtest/server-settings.json` with root-only permissions.

## Manual measurement and migration (0.5.4-L)

Use **Reporting → Speedtest → Run measurement now** to execute a one-shot test with the last saved settings. Status updates asynchronously and reports refresh after completion. Cron is unaffected.

**Full guide:** [Remove old Ookla and install LibreSpeed](MIGRATION_OOKLA_EN.md).
