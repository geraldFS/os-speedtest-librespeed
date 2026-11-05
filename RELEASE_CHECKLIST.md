# 0.5.4-L test status

- [x] Official LibreSpeed `--json` array parser regression tests (one, multiple, empty, malformed)
- [x] Source syntax and archive/manifest checks
- [x] User confirmed `configctl csvspeedtest run` succeeded on real OPNsense 26.7.8_2 with 0.5.1-L (0.5.4-L not yet tested)
- [x] User screenshot shows a LibreSpeed measurement under 0.5.1-L (0.5.4-L not yet tested)
- [ ] Test both report downloads and dashboard after successful live measurement
- [ ] Test `pkg add` / `pkg delete` for this specific build on a test system

# Release checklist — OPNsense LibreSpeed Reporting 0.5.4-L

- [x] Regression check: versioned report script and six LibreSpeed header cells align with six row values; old nine-column Volt layout is invalidated

## Reproducible local checks

- [x] PHP/JavaScript/shell syntax; XML parse
- [x] .pkg archive matches manifest (regression against old double-slash path issue)
- [x] LibreSpeed only; no Python speedtest measurement dependency
- [x] GUI Cron policy tests: fresh, idempotent, user-managed job, tagged removal
- [x] OPNsense Cron model integration simulated with mock model/config (no real system write)
- [x] Measurement and per-run provenance sidecar simulated
- [x] LibreSpeed bootstrap missing-CLI branch and hash mismatch simulated with command mocks
- [x] MIT metadata and bilingual README

- [x] CSV download handlers tested using MVC-like Response stub (bytes, headers, missing files, symlinks)
- [x] OPNsense stable/26.7 Response API source reviewed for resource streaming; no unsupported setFileToSend call remains

## Real OPNsense 26.7.8_2 VM (required before stable release)

- [ ] Verify vendor CLI install on a fresh VM without LibreSpeed, including terms acceptance
- [ ] Independently confirm `pkg add` and `pkg delete` end-to-end for this repackaged 0.5.4-L release archive
- [ ] Confirm new GUI Cron entry appears hourly under System → Settings → Cron
- [ ] Confirm existing user GUI Speedtest job is not replaced or duplicated
- [ ] Confirm previous hidden package cron is removed only when managed
- [ ] Confirm user-modified Cron job is preserved during removal
- [ ] Confirm plugin-owned Cron job is removed, config.xml and cron reloaded
- [ ] Confirm new CSV measurement and provenance use matching timestamps
- [x] User reported functional reporting page, table alignment, dashboard, and download functionality on OPNsense 26.7.8_2 (not independently reproduced)
- [ ] Independently confirm reporting table, filtered periods, charts, both CSV downloads and administrator-only clear
- [ ] Confirm `pkg delete` does not delete existing logs, provenance CSV or LibreSpeed CLI
- [ ] Test GUI on non-root, read-only and full-admin accounts (ACL/CSRF)
- [ ] Validate safe fallback in absence of configd or cron model, and firewall recovery
- [ ] Publish actual maintainer, repository URL, signed release archive and final hashes

Do not mark all items green until observed on a real system.

## Public release metadata pending / Ausstehende Angaben

- [ ] Actual GitHub repository URL and maintainer contact must be supplied before public publication.
- [ ] Confirm rightful copyright holders and existing third-party notices before asserting the MIT license covers all project code.
- [ ] Complete clean-system and uninstall tests and publish exact test environment.

## 0.5.4-L manual-run and migration checks

- [x] PHP routes `manualstart` (admin POST) and `manualstatus` (GET) present; ACL updated.
- [x] Asynchronous worker uses fixed executable and shared lock; offline success/failure/duplicate tests.
- [x] UI button, progress polling and history refresh after successful measurement.
- [x] Separate DE/EN migration guides for removing old Ookla and upgrading LibreSpeed.
- [ ] Manual click on OPNsense 26.7 with one and three servers, including a running-Cron collision.
- [ ] Real `pkg add`/upgrade/`pkg delete` on FreeBSD/OPNsense.
- [ ] Confirm historical CSV and GUI-Cron entries preserved after upgrade.
