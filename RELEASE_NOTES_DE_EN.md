# os-speedtest v0.5.4-L — Release Notes / Versionshinweise

## Deutsch

**Status:** Stabiler Community-Funktionsstand für die vom Anwender getesteten Abläufe unter OPNsense 26.7.x (amd64). Unabhängige Zertifizierung durch OPNsense oder LibreSpeed liegt nicht vor. Nichtoffizielles Plugin.

### Funktionen

- Messung mit LibreSpeed CLI 1.0.14 (separater Download, LGPL-3.0), ohne Ookla als Messengine.
- **Messung jetzt starten** in **Berichterstattung → Speedtest**, mit Statusanzeige und Aktualisierung der Auswertung.
- Durchsuchbare Testserver-Liste aus `librespeed-cli --list`; Auswahl von bis zu **drei Servern**.
- Einstellbare Reihenfolge (nacheinander/gleichzeitig), parallele HTTP-Verbindungen und Messdauer.
- Stündlicher GUI-Cronjob, CSV-Historie, Report-Diagramme, Dashboard und Versionsnachweise.
- Datenbewahrende Migration von älteren Ookla-Versionen mit separater DE/EN-Anleitung.
- Hotfixes für JSON-Array-Ausgabe von LibreSpeed und alte kompilierte Ookla-Vorlagen.

### Echte Tests vom 05.11.2026

Der Anwender bestätigt erfolgreich: frische Installation, Installation auf Bestandssystem, Auswertung, manuelle GUI-Messung, Serverauswahl und Cronjob. Eine vorgelegte Shell-Ausgabe bestätigt außerdem das erfolgreiche `pkg delete` von v0.5.4-L und das Entfernen **eines** paketverwalteten GUI-Cronjobs. Der tatsächliche Erhalt der CSV-Logdateien nach Deinstallation sowie alle Benutzerrollen wurden nicht separat nachgeprüft. Alle Details: `TEST_REPORT_DE_EN.md`.

### Installation / Update

```sh
cd /tmp
tar -xzf os-speedtest_0.5.4-L.tar.gz
cd os-speedtest_0.5.4-L
sh install.sh
```

Die vorhandene LibreSpeed-v0.5.x-Version muss für ein Upgrade nicht vorher gelöscht werden. Bei Migration von 0.4.x und Ookla bitte die gesonderte Migrationsanleitung lesen. Das paketierte LibreSpeed CLI ist **nicht** im Projektarchiv enthalten.

**Transparenz:** Der FreeBSD-Paketname bleibt `os-speedtest-csv-reporting`. Die Maintainer- und GitHub-Metadaten sind vor öffentlicher Veröffentlichung mit echten Angaben zu ergänzen; GitHub-Publikation ist nicht durch diesen Testbericht bestätigt.

---

## English

**Status:** Community-tested stable functionality for user-tested workflows on OPNsense 26.7.x (amd64). No independent OPNsense or LibreSpeed certification. Unofficial plugin.

### Features

- LibreSpeed CLI 1.0.14 measurement engine (downloaded separately, LGPL-3.0), no Ookla measurement dependency.
- **Run measurement now** from **Reporting → Speedtest**, with progress status and report refresh.
- Searchable server list retrieved by `librespeed-cli --list`, with up to **three selected servers**.
- Sequential/simultaneous modes, configurable concurrent HTTP requests and test duration.
- Hourly GUI Cron, CSV history, report charts, dashboard and provenance records.
- Bilingual migration guide to remove legacy Ookla deployments without deleting historical logs.
- Fixes for LibreSpeed JSON-array results and outdated compiled Ookla templates.

### Real-world tests, November 5, 2026

The user reported successful fresh and existing-system installation, reporting, manual GUI measurement, server selection and scheduled Cron execution. A provided shell transcript confirms successful package removal and deletion of **one** package-managed GUI Cron task. Post-uninstall CSV retention and every GUI role were not independently verified. See `TEST_REPORT_DE_EN.md` for the evidence boundaries.

### Install / upgrade

```sh
cd /tmp
tar -xzf os-speedtest_0.5.4-L.tar.gz
cd os-speedtest_0.5.4-L
sh install.sh
```

Existing LibreSpeed 0.5.x installations can be upgraded without uninstalling. Refer to the migration guide for 0.4.x and Ookla. The LGPL LibreSpeed CLI binary is not bundled.

**Publication:** FreeBSD package name is still `os-speedtest-csv-reporting`. Replace placeholder maintainer/repository metadata before public release. This report does not assert a GitHub release has been published.