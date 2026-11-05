# os-speedtest 0.5.4-L – Release Notes / Versionshinweise

## Deutsch

- Neuer Button **„Messung jetzt starten“** unter Berichterstattung → Speedtest.
- Eine manuelle Messung verwendet zuletzt gespeicherte Server-/Testeinstellungen; Cron bleibt unverändert.
- Asynchroner Messlauf mit Statusanzeige; Schutz vor doppelten manuellen Aufträgen.
- Nach Erfolg werden Tabelle und Diagramme aktualisiert.
- Zusätzliche vollständige Migrationsanleitung für Ookla und 0.4.x, mit datenschonender Entfernung.
- Die LibreSpeed-Messengine und Logformate bleiben unverändert.
- **Teststatus:** Offline-Tests bestanden; echter GUI-/Pakettest auf OPNsense 26.7 steht aus.

## English

- New **Run measurement now** button on Reporting → Speedtest.
- Uses the last saved server selection and test parameters, without changing Cron.
- Detached measurement process with progress status and duplicate-start protection.
- Refreshes report table and charts on success.
- New DE/EN migration guides to safely remove old Ookla components and 0.4.x.
- Existing LibreSpeed engine and CSV format remain unchanged.
- **Validation:** Offline checks passed; real-world OPNsense GUI and pkg tests remain pending.


### Pakethotfix zur Veröffentlichung / Package release correction

- Maintainer: `geraldFS`; Repository: https://github.com/geraldFS/os-speedtest-librespeed. Kein offizielles OPNsense- oder LibreSpeed-Paket.
- Eine Erstinstallation mit der einzelnen `.pkg` lädt die offizielle LibreSpeed CLI 1.0.14 jetzt bei Bedarf selbst herunter. Die heruntergeladene Datei wird vor der Installation anhand des SHA-256-Werts `29c645056f4bb6f4472c694d8873db083894cd816b61aca9975c6859d252630d` geprüft. Dieser neue Installationspfad ist auf einer echten OPNsense noch nicht geprüft.
- Das bereits vom Anwender getestete frühere `.pkg` wurde aufgrund dieser Korrektur neu gebaut; dessen frühere Prüfsumme gilt **nicht mehr**.

The standalone `.pkg` now downloads/checks LibreSpeed v1.0.14 when absent, without using nested pkg calls. This path still needs a real OPNsense smoke test.
