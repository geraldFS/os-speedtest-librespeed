# Testbericht / Test report — os-speedtest v0.5.4-L

**Berichtsdatum / Report date:** 2026-11-05  
**Release-Tag (geplant / planned):** `v0.5.4-L`  
**Anwendung / Application:** OPNsense 26.7.x amd64, os-speedtest v0.5.4-L, LibreSpeed CLI v1.0.14  
**Evidenzquelle / Evidence:** Benutzerangaben in der Konversation sowie ein kopiertes Terminalprotokoll; lokaler Regressionstest des Quellcodes.

## Deutsch — bestätigter Testumfang

| Prüfung | Ergebnis | Grundlage |
|---|---|---|
| Frische Installation | Bestanden laut Anwender | Aussage zur Neuinstallation |
| Upgrade / Installation auf Bestandssystem | Bestanden laut Anwender | Aussage zur Bestandsinstallation |
| LibreSpeed-Auswertung / Diagramme | Bestanden laut Anwender | Aussage zur Auswertung |
| Manueller GUI-Test | Bestanden laut Anwender | Aussage „manuel funktioniert“ |
| Serverauswahl | Bestanden laut Anwender | Aussage „Serverauswahl funktioniert“ |
| Geplanter Cronjob | Bestanden laut Anwender | Aussage „Cronjob dito“ |
| Paketdeinstallation v0.5.4-L | Bestanden laut Terminalprotokoll | `Deleting files ... 100%` |
| Entfernung paketverwalteter GUI-Cronjobs | 1 Job entfernt laut Terminalprotokoll | `Cron: 1 eindeutig paketverwaltete GUI-Jobs entfernt.` |
| CSV- und CLI-Dateien nach Deinstallation vorhanden | **Nicht gesondert bestätigt** | Deinstaller meldet nur, dass sie erhalten bleiben sollen |
| GUI-ACL / CSRF für alle Rollen | **Nicht am Gerät bestätigt** | Nur offline getestet |
| Gleichzeitiger Cron- und GUI-Start | **Nicht am Gerät bestätigt** | Nur offline simuliert |

### Offline-Regression (2026-11-05)

Erneut ausgeführt: `tests/check.py`, `test_measure_libre.py`, `test_server_selection.py`, `test_manual_run.py`, `test_cron_integration.py`, `test_cron_policy.php`, `test_csv_download.php`, PHP-Lint, Node-Syntax und Shell-Syntax. **Alle ausgeführten Prüfungen bestanden.** Das überprüft Quellcode und simulierte Aufrufe, nicht die vollständige Laufzeitumgebung einer fremden Firewall.

Das für den Anwender getestete Paket wurde bei der Dokumentationsaktualisierung **nicht verändert**: `os-speedtest_0.5.4-L.pkg` mit SHA-256 `8ede804c7e257d9e645573b61367561956e2fc2983956936727099bdd280f2a7`.

Die Migrationshinweise beschreiben eine datenbewahrende Deinstallation. **Eine separate Dateisystem-Kontrolle nach `pkg delete` liegt nicht vor.**

## English — scope and limits

The user confirmed working fresh and existing-system installations, reporting, manual GUI measurement, server selection, and automated Cron runs. A pasted OPNsense transcript independently visible in this conversation shows `pkg delete os-speedtest-csv-reporting` finishing successfully and removing one plugin-managed GUI Cron entry. A full external reproduction, real ACL tests, and inspection of retained files after uninstall were **not** provided. Local source regression tests passed on 2026-11-05; they are not equivalent to OPNsense field testing.

The tested `.pkg` bytes remain unchanged, SHA-256 `8ede804c7e257d9e645573b61367561956e2fc2983956936727099bdd280f2a7`. Package provenance and upstream licensing are documented separately.
