# os-speedtest v0.5.4-L: Kurzanleitung zur OPNsense-Installation

## Kann ich eine `.pkg` unter „System → Firmware → Erweiterungen“ hochladen?

**Nein.** In **System → Firmware → Erweiterungen** (englisch: *System → Firmware → Plugins*) zeigt OPNsense Plugins an, die aus den eingerichteten Paket-Repositories bezogen werden. Eine Upload-Funktion für beliebige lokale `.pkg`-Dateien gibt es dort nicht.

### Empfohlen: vollständigen Installer verwenden

1. Vorher die OPNsense-Konfiguration sichern.
2. `os-speedtest_0.5.4-L.tar.gz` per SCP/SFTP nach `/tmp` auf die Firewall kopieren.
3. Als `root` über SSH oder die OPNsense-Konsole ausführen:

   ```sh
   cd /tmp
   tar -xzf os-speedtest_0.5.4-L.tar.gz
   cd os-speedtest_0.5.4-L
   sh install.sh
   ```

   Der Installer prüft beziehungsweise installiert die benötigte LibreSpeed CLI und richtet die Plugin-Komponenten ein. Die LibreSpeed-Binärdatei wird separat aus dem offiziellen Upstream-Release bezogen.

4. Unter **Berichterstattung → Speedtest** die Server konfigurieren und eine manuelle Messung starten.
5. Kontrolle:

   ```sh
   pkg info os-speedtest-csv-reporting
   /usr/local/bin/librespeed-cli --version
   configctl csvspeedtest run
   tail -n 3 /var/log/librespeed.csv
   ```

### Alternativ: einzelne `.pkg` installieren

**Voraussetzung:** Die passende LibreSpeed CLI ist bereits unter `/usr/local/bin/librespeed-cli` vorhanden.

```sh
# zuvor die .pkg nach /tmp übertragen
pkg add /tmp/os-speedtest_0.5.4-L.pkg
```

Achtung: Die reine `.pkg`-Installation ist **nicht gleichwertig** mit dem vollständigen Installer, insbesondere hinsichtlich vorgelagerter Prüfungen und Einrichtung des LibreSpeed-Clients. Für eine Neuinstallation wird `sh install.sh` empfohlen.

### Künftig Installation über „Firmware → Erweiterungen“

Dazu müsste das Community-Paket in einem für OPNsense konfigurierten **pkg-Repository** veröffentlicht werden, inklusive Paketindex und Metadaten. Anschließend müsste der Administrator dieses Repository einbinden und die Paketdaten aktualisieren. Erst dann könnte der Eintrag in der Plugin-Liste erscheinen. **Ein GitHub-Release mit einer einzelnen `.pkg`-Datei reicht dafür nicht aus.**

Referenz: [OPNsense – Firmware / Plugins](https://docs.opnsense.org/manual/firmware.html).

## English (short)

OPNsense **System → Firmware → Plugins** does not offer a local `.pkg` upload option. It lists plugins from configured package repositories. For this community package, upload `os-speedtest_0.5.4-L.tar.gz` to `/tmp` via SCP/SFTP, extract it, and run `sh install.sh` as root. Direct `pkg add /tmp/os-speedtest_0.5.4-L.pkg` requires LibreSpeed CLI to be installed already and does not replace the full bootstrap installer. GUI installation through the Plugins page would require a separately configured OPNsense package repository, not just an individual GitHub release asset.
