## 0.5.4-L (2026-11-05)
- OPNsense reporting page: manual "Messung jetzt starten" button using persisted server selection.
- Asynchronous, root-owned background worker with polling status (running/success/failure); no changes to GUI Cron schedule.
- Prevent duplicate manual runs; reuse the existing exclusive lock in measure.sh for Cron coexistence.
- Security: POST with CSRF and admin check, read-only status endpoint, fixed configd actions, no arbitrary user-supplied shell commands.
- Added German migration guide (Ookla / 0.4.x removal, preservation of CSV logs) and English translation.

## 0.5.4-L
- Serverliste per `librespeed-cli --list` im GUI als durchsuchbare Tabelle.
- Bis zu drei verschiedene Server auswählbar und persistent gespeichert.
- Serverwahl automatisch oder fest, Messung nacheinander oder gleichzeitig.
- HTTP-Verbindungen (1–12) und Testdauer (5–60 s) konfigurierbar.
- Native OPNsense configd-Aktionen mit GET/POST und Administratorberechtigungen.
- Bestehende Mess-CSV, Cronjobs und LibreSpeed-Binary unverändert erhalten.

## 0.5.4-L — 2026-11-05 (UI cache hotfix)

- Fix OPNsense 26.7 compiled Volt template cache not being invalidated during upgrades. Old reporting pages showed Ookla labels although LibreSpeed measurements were already running.
- On installation, remove only cached `*csvspeedtest*` Volt files; the SSH/console bundle installer then restarts the WebGUI to invalidate PHP OPcache. Direct `pkg add` installation requires a manual WebGUI restart.
- Clean up LibreSpeed reporting hints, remove legacy server-ID/result-link text and display only the first line of the LibreSpeed CLI version.
- Rebuild the six table headers at runtime so an older compiled template cannot silently shift LibreSpeed data columns.
- Correct the package post-install cache-clearing command and test it.
- Retain LibreSpeed measurement program, CSV structure, Cron jobs and historic user data without change.
- Add regression checks for template labels and cache clearing.

## 0.5.4-L — 2026-11-05

- FIX: Parse nonempty JSON arrays from official LibreSpeed CLI `--json`; log each valid server result.
- FIX: Normalize multi-line `--version` output to one CSV-safe line.
- TEST: Add isolated CLI-JSON regression tests (array, multi-server, compatibility object, malformed data).
- No intentional change to GUI Cron jobs, logs, or Ookla legacy archives.

# Changelog / Änderungsprotokoll

## 0.5.4-L – Release-Dokumentation (2026-11-04)

- Einheitliche Veröffentlichung als `os-speedtest_0.5.4-L.*`, ohne Änderung des internen FreeBSD-Paketnamens `os-speedtest-csv-reporting`.
- Zweisprachige README und separate deutsche/englische Installationsanleitungen; Prüfsummen und GitHub-Release-Hinweise.
- Die unter OPNsense 26.7.8_2 gemeldete erfolgreiche Benutzertest-Rückmeldung wurde dokumentiert; saubere Erstinstallation und vollständiger Deinstallationstest der Version 0.5.4-L sind noch nicht unabhängig bestätigt.
- Keine Änderung an PHP-/JavaScript-/Cron-/LibreSpeed-Messlogik durch diese Release-Dokumentationsänderung.

# 0.5.4-L — Reporting table cache hotfix

- Force a versioned JavaScript resource URL on the reporting page so stale 1.2.0 table logic cannot be served with the nine-column template.
- Add a frontend version marker and a regression check for nine table columns.
- No change to Speedtest measurements, LibreSpeed CLI, CSV files, logging or Cron jobs.


## 0.5.4-L — 2026-11-04 (development hotfix)

- Fix both CSV downloads (`history/download` and `history/provenance`) after real OPNsense 26.7.8_2 log errors showed an undefined `OPNsense\Mvc\Response::setFileToSend()` method.
- Use the supported `Response::setContent($stream, true)` path and HTTP attachment headers; stream original bytes unchanged, with no CSV parsing or HTML escaping.
- Add regression tests for binary-safe delivery, both export filenames, missing files, and symbolic-link rejection. Keep all CLI, Cron, history and provenance formats unchanged.
- Verified against OPNsense `stable/26.7` `Response.php` and `ApiControllerBase.php`; real upgrade and browser-download smoke test still required.


## 0.5.4-L — 2026-11-04 (development release)

- **Version reset** from 1.4.x; direct downgrade of an installed 1.4.3 package is blocked by the bundle installer. Preserve logs and explicitly uninstall older reporting package first.
- Native OPNsense Cron model creates an editable hourly GUI job only when no other Speedtest job is detected; no hidden new cron files.
- Only exactly package-tagged GUI jobs are removed on uninstall. Other cron entries and all data remain.
- Migrate previous hidden, package-owned cron entry when safe.
- Pin identity of the measurement binary before executing the LibreSpeed speed test; record version, SHA-256, OS version and result URL in a separate CSV.
- Mock-based new CLI install and failure tests; offline CI checks; MIT license; full German and English README.
- Not yet confirmed on real OPNsense 26.7.8_2. Do not publish as stable before VM smoke tests.

### Release-build correction (2026-11-05)
- Set package metadata to unofficial project, maintainer `geraldFS`, repository `https://github.com/geraldFS/os-speedtest-librespeed`.
- Standalone `.pkg` now downloads and SHA-256-verifies the official LibreSpeed CLI on fresh installs, using a direct download inside the pre-install hook without recursion into `pkg`.
- The all-in-one `install.sh` continues to provide its already-tested bootstrap path.
- Existing LibreSpeed CLI and user CSV data are preserved. The new pkg-only bootstrap has not been validated on a real OPNsense device yet.
