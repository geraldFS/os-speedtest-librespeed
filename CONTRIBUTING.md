# Contributing / Mitwirken

## Deutsch

Beiträge zu Code, Tests und Dokumentation sind willkommen. Vor einer Pull-Request bitte `python3 build_pkg.py`, `python3 tests/check.py` sowie die in `.github/workflows/validate.yml` aufgeführten Testskripte ausführen. Änderungen an Cron, Paket-Hooks, API oder Datenlöschung immer mit nachvollziehbaren Tests und Beschreibung der Datensicherheit belegen.

Keine proprietären Ookla-Binärdateien, privaten CSV-Logs, Zugangsdaten oder ungefilterten Firewall-Diagnoseberichte committen. Für API- und Installationsänderungen möglichst eine isolierte OPNsense-26.7-Testumgebung einsetzen. Ein Maintainer und eine konkrete Repository-Adresse müssen vor Veröffentlichung benannt werden.

## English

Contributions to code, tests and documentation are welcome. Before submitting a pull request, run `python3 build_pkg.py`, `python3 tests/check.py`, and the tests listed in `.github/workflows/validate.yml`. Changes involving Cron, package hooks, APIs or log deletion should include test evidence and notes on preserving user data.

Never commit proprietary Ookla binaries, private measurement CSV files, credentials or unredacted firewall diagnostics. Prefer an isolated OPNsense 26.7 VM for install and API changes. Maintainer: geraldFS; repository: https://github.com/geraldFS/os-speedtest-librespeed.
