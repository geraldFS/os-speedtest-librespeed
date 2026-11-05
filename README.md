# os-speedtest 0.5.4-L — OPNsense LibreSpeed Reporting

[Deutsch](#deutsch) · [English](#english)

---

## Deutsch

**Community-Plugin für OPNsense 26.7.x / amd64.** Ausschließlich LibreSpeed CLI, kein Ookla-Messclient. Projektcode: MIT; LibreSpeed CLI: LGPL-3.0. Kein offizielles OPNsense- oder LibreSpeed-Projekt.

### Was ist neu in 0.5.4-L?

**Messparser aus 0.5.1-L:** LibreSpeed CLI 1.0.14 gibt mit `--json` eine Liste von Messergebnissen zurück – auch bei nur einem Messserver. In 0.5.0-L erwartete der Parser fälschlich ein einzelnes Objekt, wodurch `configctl csvspeedtest run` mit `Error (1)` abbrach und die WebGUI keine LibreSpeed-CSV fand. Die neue Version liest die Liste korrekt und kann mehrere Ergebnisse protokollieren. Ungültige oder leere Ergebnisse werden abgewiesen. Die Version wird einzeilig protokolliert.

**UI-Hotfix 0.5.4-L:** Entfernt alte kompilierte OPNsense-Volt-Vorlagen nach dem Update und stellt sicher, dass Tabellenüberschriften und Datenspalten immer übereinstimmen (sechs LibreSpeed-Spalten). Außerdem wird die CLI-Version nur in der ersten Zeile angezeigt.

**Teststand (0.5.4-L):** Die LibreSpeed-Messaktion aus 0.5.1-L wurde am 5.11.2026 auf OPNsense 26.7.8_2 mit `configctl csvspeedtest run` erfolgreich gestartet und im Screenshot waren Messwerte sichtbar. Die Installation und GUI-Anzeige von 0.5.4-L sind noch nicht auf dem realen Gerät bestätigt.

### Neu: manuelle Messung über die Berichtsseite

**„Messung jetzt starten“** führt einen unabhängigen LibreSpeed-Messlauf mit der zuletzt **gespeicherten** Serverkonfiguration aus. Der Auftrag läuft im Hintergrund; die Weboberfläche zeigt den Status und aktualisiert Tabelle/Diagramme nach Abschluss. Der vorhandene Cron-Zeitplan wird nicht verändert. Für bis zu drei Server im Modus „Nacheinander“ kann eine Messung mehrere Minuten dauern.

**Migration von Ookla / alten Plugin-Versionen:** [Schritt-für-Schritt-Anleitung](docs/MIGRATION_OOKLA_DE.md).

### Funktionen

- **Berichterstattung → Speedtest:** Tabelle, 24 Stunden / 7 Tage / alle Messungen, CSV-Download und geschütztes Leeren mit Backup.
- **Lobby → Dashboard:** Diagramme für Download/Upload und Ping/Jitter; Paketverlust wird nicht erfunden.
- **LibreSpeed CLI 1.0.14:** Automatischer Download vom offiziellen GitHub-Release durch den Komplett-Installer, mit SHA-256-Prüfung. Das CLI-Binary wird nicht im Projektarchiv mitgeliefert.
- **Cron:** Stündlicher GUI-Auftrag, sofern kein bestehender Speedtest-Auftrag erkannt wird. Bestehende Benutzeraufträge werden nicht verändert.
- **Nachvollziehbarkeit:** Separate CSV für verwendeten Messserver, CLI-Version, SHA-256 und OPNsense-Version.

### Installation oder Update von 0.5.0-L / 0.5.1-L

Konfiguration sichern. Das **TAR.GZ-Komplettarchiv** nach `/tmp` übertragen, anschließend auf OPNsense als root:

```sh
cd /tmp
tar -xzf os-speedtest_0.5.4-L.tar.gz
cd os-speedtest_0.5.4-L
sh install.sh
```

**Version 0.5.0-L oder 0.5.1-L nicht vorher deinstallieren.** Der Installer prüft die vorhandene LibreSpeed-CLI und führt ein Paketupdate durch. Das einzelne `.pkg` setzt ein vorhandenes LibreSpeed CLI voraus und wird mit `pkg add ./os-speedtest_0.5.4-L.pkg` installiert.

### Prüfung und Fehlerdiagnose

```sh
pkg info os-speedtest-csv-reporting
/usr/local/bin/librespeed-cli --version
configctl csvspeedtest run
tail -n 4 /var/log/librespeed.csv
tail -n 10 /var/log/librespeed-error.log
```

Bei einem weiteren `Error (1)` sind vor allem die Zeilen aus `librespeed-error.log` aussagekräftig. **Nicht** in kurzen Abständen wiederholt Bandbreitentests starten. Eine einzelne manuelle Messung genügt zur Überprüfung.

Erwartete Dateien:

- `/var/log/librespeed.csv` — `Timestamp,ServerName,ServerURL,Download_Mbps,Upload_Mbps,Ping_ms,Jitter_ms,CLI_Version`
- `/var/log/librespeed_provenance.csv` — Zeit, Version, SHA-256 des CLI, OPNsense-Version, Serverdetails

Alte historische CSV-Dateien werden nicht geändert oder gelöscht. Die Messdaten sind keine amtlichen Provider-Nachweise.

### Deinstallation

```sh
pkg delete os-speedtest-csv-reporting
```

Messdaten und das separat installierte LibreSpeed CLI bleiben dabei erhalten. Die Messwerte werden nicht mit den früheren Ookla-Messungen vermischt.

Die ausführliche [deutsche Installationsanleitung](docs/INSTALLATION_DE.md) beschreibt auch den Dateitransfer, Prüfsummen und Fehlerbehandlung.

### Lizenz

Der eigene Plugin-Code steht unter [MIT](LICENSE). Das separat bezogene [LibreSpeed CLI](https://github.com/librespeed/speedtest-cli) ist LGPL-3.0-lizenziert und wird hier nicht weiterverteilt. Das Paket ist ein nicht signiertes Community-Paket. Die unveränderte, in der Praxis getestete Paketdatei enthält noch Maintainer-Platzhalter. Ein Paketupdate mit korrigierten Metadaten ist vorgesehen.

---

## English

**Community plugin for OPNsense 26.7.x / amd64.** LibreSpeed CLI only; no Ookla measurement engine. Project code: MIT; LibreSpeed CLI: LGPL-3.0. Not endorsed by OPNsense or LibreSpeed.

### What's new in 0.5.4-L?

**Parser fix inherited from 0.5.1-L:** Official LibreSpeed CLI 1.0.14 emits a JSON **array** with `--json`, even for a single tested server. Version 0.5.0-L expected an object, causing `configctl csvspeedtest run` to fail and leaving the GUI without an output CSV. The parser now accepts the array and multiple report entries, rejecting empty or invalid data. CLI version information is written on a single line.

**UI hotfix 0.5.4-L:** Remove stale compiled OPNsense Volt templates after upgrading and render the six LibreSpeed table headers directly from the current field layout. The CLI version display is limited to the first line.

**Validation:** The 0.5.1-L LibreSpeed action was successfully run on OPNsense 26.7.8_2 on November 5, 2026, and the user supplied a screenshot showing values. Installation and rendered UI behavior of 0.5.4-L have not yet been verified on the live firewall.

### Manual measurement from the WebGUI

**Run measurement now** starts a one-time LibreSpeed test using the last **saved** server selection. It runs asynchronously with a status indicator and refreshes reports on completion without changing Cron. See the [Ookla-to-LibreSpeed migration guide](docs/MIGRATION_OOKLA_EN.md).

### Features

- **Reporting → Speedtest:** Historical table, 24-hour / 7-day / all filters, CSV export, admin-only clearing with backup.
- **Lobby → Dashboard:** Download/upload and ping/jitter charts. Packet loss is marked unavailable rather than fabricated.
- **LibreSpeed CLI 1.0.14:** Full installer downloads upstream FreeBSD amd64 release and checks SHA-256; CLI executable is not redistributed.
- **Cron:** Create an hourly GUI task only when no existing speedtest task is detected; preserve user-defined tasks.
- **Provenance:** CSV with per-measurement server, CLI version, SHA-256 and OPNsense version.

### Install / upgrade from 0.5.0-L / 0.5.1-L

Back up your firewall configuration, copy the release TAR.GZ to `/tmp`, then run as root:

```sh
cd /tmp
tar -xzf os-speedtest_0.5.4-L.tar.gz
cd os-speedtest_0.5.4-L
sh install.sh
```

**Do not uninstall 0.5.0-L or 0.5.1-L first.** The installer checks LibreSpeed and upgrades the installed package. The standalone `.pkg` requires an already installed LibreSpeed CLI and can be installed with `pkg add ./os-speedtest_0.5.4-L.pkg`.

### Verify / troubleshoot

```sh
pkg info os-speedtest-csv-reporting
/usr/local/bin/librespeed-cli --version
configctl csvspeedtest run
tail -n 4 /var/log/librespeed.csv
tail -n 10 /var/log/librespeed-error.log
```

If the run still reports `Error (1)`, inspect `librespeed-error.log`; do not repeatedly trigger speed tests. Data is stored separately from legacy Ookla CSV history. These logs are not regulatory evidence of a contractual shortfall.

### Uninstall / licensing

```sh
pkg delete os-speedtest-csv-reporting
```

Logs and the separately installed LibreSpeed CLI are retained. Plugin code is [MIT licensed](LICENSE). The upstream [LibreSpeed CLI](https://github.com/librespeed/speedtest-cli) is licensed under LGPL-3.0, and is not bundled. This is an unsigned community package; the previously field-tested package still contains maintainer placeholders; correcting package metadata requires rebuilding and revalidation.

See the complete [English installation instructions](docs/INSTALLATION_EN.md).

### 0.5.4-L — UI-Cache / Template cache

Deutsch: Beim Upgrade wird die veraltete kompilierte Speedtest-Berichtsseite gezielt aus dem Volt-Cache entfernt. Der SSH-Installer startet die WebGUI neu; Messdaten und Cronjobs bleiben unverändert.

English: During upgrades only the plugin-specific compiled Volt view is purged. The SSH installer restarts WebGUI, preserving speed test histories and Cron settings.

## LibreSpeed-Serverauswahl (0.5.4-L) / Server selection

**Deutsch:** Unter **Berichterstattung → Speedtest → Messserver & Testeinstellungen** zeigt
das Plugin die Live-Liste von `librespeed-cli --list` in einer Tabelle. Maximal drei
Server lassen sich auswählen. Die Einstellungen (automatische/feste Auswahl,
nacheinander/gleichzeitig, 1–12 HTTP-Verbindungen, 5–60 Sekunden Messdauer)
werden unter `/usr/local/etc/os-speedtest/server-settings.json` mit Modus 0600
gespeichert. Cron und manuelle Messungen benutzen dieselben Werte. Das Plugin
führt keine unbegrenzten Serververgleiche im Hintergrund aus. Drei parallele
Messungen teilen die Anschlussbandbreite; als Vergleichsmessung „Nacheinander“
wählen. Kein automatischer Ersatzserver bei Ausfall. Der Abruf der öffentlichen
Liste benötigt Zugriff auf `https://librespeed.org`.

**English:** Open **Reporting → Speedtest → Measurement servers & settings**
(the GUI labels are currently German) to load the live server list using the CLI's
`--list` option. Select up to three servers. Settings are stored in a root-only
local JSON file and apply to manual and scheduled tests. Choose sequential for
comparable independent throughput results; parallel is a contention / load test.
The list is fetched on request, and selections are strictly validated.

**Important:** The new config JSON is user data, not part of the package manifest;
therefore the package manager does not delete it during routine upgrades.