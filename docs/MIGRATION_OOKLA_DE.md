# Migration: Ookla und alte os-speedtest-Versionen entfernen, LibreSpeed installieren

**Gilt für:** OPNsense 26.7.x / amd64, `os-speedtest` **0.5.4-L**. Diese Anleitung unterscheidet zwischen dem **alten Plugin** (`os-speedtest-csv-reporting`) und dem **Ookla-Messprogramm** (`/usr/local/bin/speedtest`). Nicht jedes System hat beides über `pkg` installiert.

> **Wichtig:** Vorher die OPNsense-Konfiguration über die WebGUI sichern. Die vorhandenen CSV-Messdaten sollen erhalten bleiben. Alle Befehle unten werden als `root` per SSH/Konsole ausgeführt. Bei Unsicherheit erst nur die Prüfkommandos ausführen.

## 1. Vorhandenen Stand und historische Messungen sichern

```sh
opnsense-version
pkg info os-speedtest-csv-reporting || true
/usr/local/bin/speedtest --version 2>/dev/null || true
/usr/local/bin/librespeed-cli --version 2>/dev/null || true
ls -lh /var/log/speedtest*.csv /var/log/librespeed*.csv 2>/dev/null
```

Optional alte Messungen vor dem Umstieg sichern (existierende Dateien bleiben auch danach erhalten):

```sh
mkdir -p /root/speedtest-migration-backup
for f in /var/log/speedtest.csv /var/log/speedtest_provenance.csv /var/log/librespeed.csv /var/log/librespeed_provenance.csv; do
  [ ! -f "$f" ] || cp -p "$f" /root/speedtest-migration-backup/
done
```

Diese Sicherung liegt auf derselben Firewall. Für ein unabhängiges Backup zusätzlich per SCP auf ein anderes System übertragen.

## 2. Alte Cronjobs deaktivieren

Unter **System → Einstellungen → Cron** alle vorhandenen Aufträge prüfen. Alte Ookla-Aufträge deaktivieren oder entfernen, insbesondere solche mit `speedtest_cron.sh` oder dem früheren "Ookla Speedtest CSV Logger". Den LibreSpeed-Cronjob erhalten. Ein manueller Test über die neue GUI **ändert den Cronjob nicht**.

Zur Kontrolle in der Shell:

```sh
grep -RniE 'ookla|speedtest_cron|csvspeedtest|librespeed' \
  /etc/crontab /usr/local/etc/cron.d /var/cron/tabs 2>/dev/null || true
```

Die Ausgabe kann auch reguläre Plugin-Aktionen enthalten: Nicht pauschal löschen. Entscheidend ist, ob der jeweilige Cron-Eintrag aktiv ist.

## 3. Altes Plugin entfernen oder ein bestehendes LibreSpeed-Plugin aktualisieren

Aktuellen Stand lesen:

```sh
pkg query '%n %v' os-speedtest-csv-reporting 2>/dev/null || true
```

- Bei **0.4.x (Ookla-Plugin)**: Die bestehende Konfiguration sichern und anschließend gezielt das alte Plugin entfernen:

  ```sh
  pkg delete os-speedtest-csv-reporting
  ```

- Bei **0.5.0-L bis 0.5.3-L (LibreSpeed)**: **Nicht deinstallieren.** Der Komplett-Installer aktualisiert die vorhandene Version und erhält bestehende Servereinstellungen und Messdateien.
- Wenn das Paket nicht installiert ist: diesen Schritt überspringen.

`pkg delete` entfernt die paketverwalteten Plugin-Dateien. Die alte Ookla-CLI ist ein **getrenntes Programm**. Die Messdateien `/var/log/speedtest.csv` usw. bleiben nach dem vorgesehenen Plugin-Hook erhalten; unabhängig davon sollten sie bereits gesichert sein.

## 4. Ookla CLI getrennt und sicher entfernen

Zunächst ermitteln, wem die Programmdatei gehört:

```sh
pkg which /usr/local/bin/speedtest
```

**Fall A – die Datei gehört einem installierten FreeBSD-Paket:** Den dort angezeigten exakten Paketnamen notieren. Vor der Entfernung dessen Abhängigkeiten und mögliche weitere Nutzung prüfen. Dann nur dieses identifizierte Ookla-Paket mit `pkg delete PAKETNAME` entfernen. **Nicht** blind andere Speedtest-Pakete oder Abhängigkeiten deinstallieren.

**Fall B – `pkg which` kennt die Datei nicht:** Die manuell installierte Binärdatei zunächst lediglich deaktivieren:

```sh
if [ -f /usr/local/bin/speedtest ] && [ ! -L /usr/local/bin/speedtest ]; then
  mv /usr/local/bin/speedtest /usr/local/bin/speedtest.ookla-disabled
fi
```

Nach erfolgreicher LibreSpeed-Messung kannst du diese Sicherheitskopie auf Wunsch endgültig löschen:

```sh
rm -i /usr/local/bin/speedtest.ookla-disabled
```

Ein früher selbst erstelltes Skript unter `/usr/local/bin/speedtest_cron.sh` oder die frühere Datei `actions_speedtest.conf` **nur dann** entfernen, wenn du deren Inhalt überprüft hast und sicher bist, dass kein verbleibender Cronjob sie verwendet. Im Zweifel erst umbenennen, nicht sofort löschen.

Das neue LibreSpeed-Plugin entfernt Ookla bewusst **nicht automatisch**, da nicht erkennbar ist, ob andere Anwendungen die alte Binärdatei verwenden.

## 5. LibreSpeed 0.5.4-L komplett installieren

Auf deinem PC die Datei `os-speedtest_0.5.4-L.tar.gz` herunterladen, ihre Prüfsumme aus der beiliegenden SHA-256-Liste prüfen und nach `/tmp` übertragen (Firewall-IP anpassen):

```powershell
scp .\os-speedtest_0.5.4-L.tar.gz root@FIREWALL-IP:/tmp/
```

Auf der OPNsense:

```sh
cd /tmp
tar -xzf os-speedtest_0.5.4-L.tar.gz
cd os-speedtest_0.5.4-L
sh install.sh
```

Der Installer erkennt eine vorhandene offizielle LibreSpeed-CLI oder lädt diese – falls erforderlich – aus dem offiziellen LibreSpeed-Release und prüft deren SHA-256-Wert. Er installiert **keine** Python-Speedtest-Implementierung und kein Ookla-CLI. Das separat verfügbare `.pkg` setzt das LibreSpeed-CLI bereits voraus.

## 6. Konfigurieren und manuell messen

1. Nach der Installation die OPNsense-WebGUI neu anmelden; **Berichterstattung → Speedtest** öffnen.
2. **Serverliste aktualisieren**, bis zu drei Server auswählen, Modus **Ausgewählte Server** und **Nacheinander** (für vergleichbare Messungen) einstellen.
3. Verbindungen und Dauer wählen, **Einstellungen speichern** anklicken.
4. **Messung jetzt starten** anklicken. Die Seite zeigt den Status ohne lange blockierende HTTP-Anfrage. Ein zweiter Start während eines laufenden Tests wird abgewiesen.
5. Nach Erfolg werden Tabelle und Diagramme aktualisiert.

Ein manueller Test verwendet die **gespeicherte** Konfiguration; ungespeicherte Änderungen wirken sich nicht aus. Gleichzeitige Tests gegen mehrere Server sind Belastungstests und teilen sich die vorhandene Internetbandbreite.

## 7. Installation und Cronjob prüfen

```sh
pkg info os-speedtest-csv-reporting
/usr/local/bin/librespeed-cli --version
sh /usr/local/opnsense/speedtest-csv-dashboard/status.sh
tail -n 5 /var/log/librespeed.csv
```

Unter **System → Einstellungen → Cron** kontrollieren, dass **nur ein gewünschter LibreSpeed-Messjob** aktiv ist. Der manuelle Messbutton ändert dessen Zeitplan nicht. Bei Messfehlern:

```sh
tail -n 20 /var/log/librespeed-error.log
```

**Fehlersuche:** Bei fehlendem Menüeintrag neu anmelden und Browser hart aktualisieren. Eine fehlende LibreSpeed-CSV bedeutet häufig, dass bisher noch keine Messung erfolgreich protokolliert wurde. Nicht mehrfach unmittelbar hintereinander testen.

## 8. Deinstallation und Datenerhalt

```sh
pkg delete os-speedtest-csv-reporting
```

Die Plugin-Dateien werden entfernt. Historische CSV-Dateien und die separat installierte LibreSpeed-CLI werden durch die vorgesehenen Paket-Hooks nicht gelöscht. Benutzerdefinierte Cronjobs sind separat zu prüfen. Vor einer öffentlichen Veröffentlichung müssen auch Upgrade und Deinstallation auf einer Test-OPNsense validiert werden.

**Nachweise:** CSV-Messwerte sind technische Verlaufsdaten und keine amtlichen Nachweise einer Minderleistung gegenüber dem Provider.