# Security / Sicherheit

## Deutsch

Dies ist ein inoffizielles Community-Projekt, das mit Root-Rechten auf einer Firewall installiert wird. **Skripte vor der Ausführung prüfen und zunächst eine Test-VM verwenden.** GitHub-Releases ohne Signatur sind nicht automatisch authentisch; die beigefügten SHA-256-Prüfsummen belegen nur die Integrität einer konkret bezogenen Datei.

CSV-Exporte, Latenzmessungen, Versionsinformationen und Ookla-Ergebnis-URLs können betriebliche Informationen enthalten. Diagnoseberichte vor öffentlichem Teilen um IP-Adressen, MAC-Adressen, Schlüssel und andere sensible Daten bereinigen.

Das Ookla-Binary ist proprietär und nicht Bestandteil des Repositories. Der Komplett-Installer lädt es bei Bedarf nach vorheriger Zustimmung und prüft den bekannten Anbieter-Paket-Hash. Fremde Paket-Repositories für FreeBSD sollten in OPNsense nicht hinzugefügt werden.

**Sicherheitsmeldung:** Vor Einrichtung eines Repositorys existiert noch keine konkrete Kontaktadresse. Bei Veröffentlichung einen GitHub-Security-Advisory-Kanal oder eine Maintainer-Adresse hinterlegen. Bis dahin keine vertraulichen Exploit-Details in öffentliche Issues posten.

## English

This is an unofficial community plugin installed with root privileges on a firewall. **Review scripts before running and test on an isolated VM.** SHA-256 checksums show file integrity, not publisher authenticity; unsigned GitHub releases are not automatically trusted.

Measurement CSV, CLI version evidence and Ookla result URLs can reveal operational information. Redact IP/MAC addresses, keys and other sensitive data before public bug reports.

The proprietary Ookla executable is not in this repository. The full installer may download it after explicit consent and verifies the pinned vendor package hash. Do not enable unofficial FreeBSD repositories on OPNsense.

**Security reporting:** No verified maintainer address or repository URL is provided yet. Before publishing, configure a GitHub Security Advisories contact path or maintainer contact. Avoid public issues containing exploit details until a private channel exists.
