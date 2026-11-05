# GitHub-Veröffentlichung / GitHub publication — os-speedtest 0.5.4-L

## Deutsch

### Repository vorbereiten

1. Neues Repository mit einem geeigneten Namen wie `os-speedtest` in deinem eigenen GitHub-Konto anlegen. Eine URL ist **noch nicht bekannt** und wird bewusst nicht erfunden.
2. Quellcode aus dem Projektverzeichnis `os-speedtest_0.5.4-L/` in das Repository übernehmen (einschließlich `src/`, `scripts/`, `hooks/`, `tests/`, `.github/`, `README.md`, `LICENSE`, `CHANGELOG.md` und Dokumentation).
3. **Vor dem Veröffentlichen** Copyright-Hinweise in `LICENSE` und Projekt-Rechteinhaberschaft prüfen; den tatsächlichen Maintainer und die Repository-URL in `build_pkg.py` und `build-native-pkg.sh` hinterlegen. Nicht behaupten, die MIT-Lizenz decke das LGPL-3.0-LibreSpeed CLI ab.
4. `dist/*.pkg` nicht als Quellcodedatei committen; `.gitignore` schließt Release-Artefakte aus. Das Paketrelease gehört in GitHub **Releases**.
5. CI-Workflow `.github/workflows/validate.yml` aktivieren. Dieser testet Syntax und die Paket-/Messlogik, **nicht** einen echten OPNsense-Installationslauf.
6. In einer frischen OPNsense-26.7-VM `pkg add`, `pkg delete`, GUI-Cron, automatische LibreSpeed-Installation, CSV-Download und Datenerhalt prüfen. Den Teststand transparent dokumentieren.

### Release erstellen

1. Git-Tag `v0.5.4-L` und GitHub Release `v0.5.4-L` anlegen (als **Pre-release**, solange vollständige Tests offen sind).
2. Als Assets hochladen: `os-speedtest_0.5.4-L.pkg`, `os-speedtest_0.5.4-L.tar.gz`, `os-speedtest_0.5.4-L.zip`, `os-speedtest_0.5.4-L_SHA256SUMS.txt`.
3. Inhalte von `RELEASE_NOTES_DE_EN.md` als Release-Beschreibung verwenden.
4. Version und SHA-256-Prüfsummen nach Upload gegen veröffentlichte Assets prüfen. Keine fremden LibreSpeed-Binärdateien mitliefern.
5. Für Integrität und Vertrauen später einen signierten Release-Prozess vorsehen; SHA-256 allein authentifiziert den Herausgeber nicht.

**Wichtig:** Der interne Paketname ist `os-speedtest-csv-reporting`; er wird nicht allein aufgrund der neuen Download-Dateinamen geändert. Ein späterer echter Paket-Rename braucht eine eigene Migrationsstrategie.

## English

### Prepare the repository

1. Create a repository under your own GitHub account, e.g. `os-speedtest`. The actual repository URL is **not yet provided**.
2. Commit the project files from `os-speedtest_0.5.4-L/`, including `src/`, `scripts/`, `hooks/`, `tests/`, `.github/`, `README.md`, `LICENSE`, `CHANGELOG.md` and docs.
3. Before publishing, verify copyright ownership and MIT licensing scope; set the actual maintainer and repository URL in `build_pkg.py` and `build-native-pkg.sh`. Do not claim the LGPL-3.0 LibreSpeed CLI is MIT licensed.
4. Do not commit built `dist/*.pkg` files to Git; upload build artifacts to GitHub Releases. The `.gitignore` excludes them.
5. Enable `.github/workflows/validate.yml`. This validates source and packaging logic but does **not** substitute for installing on actual OPNsense.
6. Test `pkg add`, `pkg delete`, GUI cron, first-time LibreSpeed provisioning, CSV exports and log preservation on a clean OPNsense 26.7 VM. Publish the real test results.

### Publish a GitHub Release

1. Create tag `v0.5.4-L` and release `v0.5.4-L`, marked **Pre-release** until full tests pass.
2. Upload assets: `os-speedtest_0.5.4-L.pkg`, `os-speedtest_0.5.4-L.tar.gz`, `os-speedtest_0.5.4-L.zip`, `os-speedtest_0.5.4-L_SHA256SUMS.txt`.
3. Use `RELEASE_NOTES_DE_EN.md` for the release description.
4. Recheck version and SHA-256 of uploaded assets. Never redistribute the LGPL-3.0 LibreSpeed executable.
5. Consider signed releases for authenticity; hashes alone do not authenticate a publisher.

**Note:** The internal pkg name stays `os-speedtest-csv-reporting` for upgrade compatibility. A later actual package rename would need a migration plan.
