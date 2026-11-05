# Installation – os-speedtest 0.5.4-L (Deutsch)

**System:** OPNsense 26.7.x, amd64. **Messprogramm:** ausschließlich LibreSpeed CLI 1.0.14 (LGPL-3.0). Die Version übernimmt den JSON-Parserfix aus 0.5.1-L und korrigiert die Spaltenüberschriften durch gezieltes Leeren des OPNsense-Volt-Caches und sechs feste LibreSpeed-Spalten.

## Voraussetzungen

- OPNsense-Konfiguration sichern und alten Ookla-Cronjob deaktivieren (falls noch vorhanden).
- `root`-Zugang per SSH oder Konsole.
- Bei fehlendem LibreSpeed CLI Netzwerkzugriff auf das offizielle GitHub-Release.
- Das Releasearchiv samt SHA-256 vor der Installation kontrollieren.

## Komplett-Installer (auch Update von 0.5.0-L oder 0.5.1-L)

Auf dem PC nach dem Download im Ordner mit der Datei:

```powershell
scp .\os-speedtest_0.5.4-L.tar.gz root@FIREWALL-IP:/tmp/
```

Dann auf OPNsense:

```sh
cd /tmp
tar -xzf os-speedtest_0.5.4-L.tar.gz
cd os-speedtest_0.5.4-L
sh install.sh
```

**Bei einem Update von 0.5.0-L oder 0.5.1-L nichts deinstallieren.** Der Paketinstaller übernimmt vorhandene Messdateien und Cronjobs. Der Paketname ist weiterhin `os-speedtest-csv-reporting`.

## Funktionstest

```sh
pkg info os-speedtest-csv-reporting
/usr/local/bin/librespeed-cli --version
configctl csvspeedtest run
tail -n 5 /var/log/librespeed.csv
tail -n 10 /var/log/librespeed-error.log
```

Der manuelle `configctl`-Aufruf führt eine echte Messung aus und kann die Leitung kurzfristig auslasten. Nicht wiederholt starten. Die CSV-Datei wird erst nach einer erfolgreichen Messung angelegt.

Danach **Berichterstattung → Speedtest** und **Lobby → Dashboard** öffnen; unter **System → Einstellungen → Cron** sicherstellen, dass nur ein LibreSpeed-Job aktiv ist.

## Falls die GUI weiterhin „LibreSpeed-CSV fehlt oder ist nicht lesbar“ meldet

1. `tail -n 15 /var/log/librespeed-error.log` aufrufen und die konkrete Fehlermeldung prüfen.
2. `ls -l /var/log/librespeed.csv` prüft die Existenz und Dateirechte.
3. Bei `Error (1)` nicht wiederholt Messungen auslösen; mögliche Netz-/Testserverfehler erst analysieren.
4. Testen, ob `configctl csvspeedtest info` funktioniert (keine Messung).

## Deinstallation

```sh
pkg delete os-speedtest-csv-reporting
```

Messdaten, CLI und benutzerdefinierte Cronjobs werden nicht absichtlich entfernt. Auf einem Produktivsystem vorher die OPNsense-Konfiguration sichern. Die vollständige Lizenzinformation findest du in der README.

## Falls weiterhin eine alte Ookla-Berichtsseite erscheint

Die neue `index.volt`-Vorlage ist in Version 0.5.4-L enthalten. Das Installationsskript entfernt den kompilierten Cache und startet die WebGUI neu. Bei direktem `pkg add` aus der Shell anschließend:

```sh
find /var/lib/php/cache -maxdepth 1 -type f -iname '*csvspeedtest*' -print
find /var/lib/php/cache -maxdepth 1 -type f -iname '*csvspeedtest*' -delete
configctl webgui restart
```

Neu anmelden und Browser mit Strg+Umschalt+R aktualisieren. Keine Mess-CSV oder Cronjobs werden gelöscht.

### Serverwahl (ab 0.5.4-L)

1. In **Berichterstattung → Speedtest** die **Messserver & Testeinstellungen** öffnen.
2. **Serverliste aktualisieren** anklicken (führt `librespeed-cli --list` aus).
3. Optional nach Ort, Anbieter oder ID filtern und maximal drei Häkchen setzen.
4. „Ausgewählte Server“ wählen, Messart **Nacheinander** (empfohlen) oder **Gleichzeitig** (Belastungstest), Verbindungen und Dauer einstellen.
5. **Einstellungen speichern**. Die nächste Cron-/manuelle Messung verwendet die Konfiguration.

Die Konfiguration liegt in `/usr/local/etc/os-speedtest/server-settings.json` (nur root);
Messdaten unter `/var/log/librespeed.csv` werden nicht angetastet.

## Manueller Messbutton und Migration (0.5.4-L)

Unter **Berichterstattung → Speedtest** mit **„Messung jetzt starten“** einen Test mit der zuletzt gespeicherten Serverauswahl auslösen. Status wird im Browser angezeigt; nach Abschluss werden Tabelle und Diagramme aktualisiert. Cron bleibt unverändert.

**Ausführliche Anleitung:** [Ookla und alte Plugin-Version entfernen / LibreSpeed installieren](MIGRATION_OOKLA_DE.md).
