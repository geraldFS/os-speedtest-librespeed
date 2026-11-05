#!/bin/sh
# ALL-IN-ONE installer for OPNsense 26.7 amd64: actual pkg + official LibreSpeed + cron.
# Run from the extracted release archive as root: sh install.sh
set -eu
umask 077
ROOT=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
NAME=os-speedtest-csv-reporting
PKG="$ROOT/dist/$NAME-0.5.4-L.pkg"
BACKUPBASE=/usr/local/opnsense/speedtest-csv-dashboard/pkg-migrations

fail() { echo "FEHLER: $*" >&2; exit 1; }
[ "$(id -u)" -eq 0 ] || fail 'Bitte als root starten.'
case "$(opnsense-version 2>/dev/null || true)" in *26.7.*) ;; *) fail 'Nur OPNsense 26.7.x';; esac
[ "$(uname -m)" = amd64 ] || fail 'Nur amd64.'
[ -f "$PKG" ] || fail "Paketdatei fehlt: $PKG"
command -v pkg >/dev/null 2>&1 || fail 'FreeBSD pkg nicht vorhanden.'
command -v sha256 >/dev/null 2>&1 || fail 'FreeBSD sha256 fehlt.'

# Verify checksums of source and *binary package* before running any installer.
[ -f "$ROOT/CHECKSUMS.sha256" ] || fail 'CHECKSUMS.sha256 fehlt.'
while read -r expected rel; do
    [ -n "$expected" ] || continue
    [ -f "$ROOT/$rel" ] || fail "Datei fehlt: $rel"
    actual=$(sha256 -q "$ROOT/$rel")
    [ "$actual" = "$expected" ] || fail "Pruefsumme falsch: $rel"
done < "$ROOT/CHECKSUMS.sha256"

# 0.5.4-L version resets the old 1.4.x version series. Refuse silent
# downgrades: old package must be removed explicitly (data files are retained).
CURRENT=$(pkg query '%v' "$NAME" 2>/dev/null || true)
if [ -n "$CURRENT" ] && [ "$(pkg version -t "$CURRENT" '0.5.4-L')" = '>' ]; then
    fail "Version $CURRENT ist bereits installiert. Vor 0.5.4-L erst Konfiguration sichern und pkg delete $NAME ausfuehren (Messdaten bleiben erhalten)."
fi

# Ensure legitimate CLI, without installing Python's different 'speedtest-cli'.
sh "$ROOT/scripts/install-librespeed.sh" || fail 'LibreSpeed CLI konnte nicht eingerichtet werden.'

mkdir -p "$BACKUPBASE"
chmod 0700 "$BACKUPBASE"
SNAP="$BACKUPBASE/$(date +%Y%m%d-%H%M%S)-$$"
mkdir -m 0700 "$SNAP"
# Snapshot previous manually installed files (v1.2.0 etc.) before pkg assumes ownership.
# No symlink traversal, no copying of sensitive measurement data into release artifacts.
count=0
while IFS='|' read -r source dest; do
    [ -n "$source" ] || continue
    count=$((count + 1))
    case "$dest" in /usr/local/opnsense/*) ;; *) fail "Ungueltiger Zielpfad: $dest";; esac
    [ ! -L "$dest" ] || fail "Symlink als Installationsziel: $dest"
    if [ -f "$dest" ]; then
        cp -p "$dest" "$SNAP/file-$count"
    else
        : > "$SNAP/absent-$count"
    fi
done < "$ROOT/manifest.txt"
cp "$ROOT/manifest.txt" "$SNAP/manifest.txt"
echo "Alte Dateien gesichert: $SNAP"

if pkg info -q "$NAME" >/dev/null 2>&1; then
    echo 'Upgrade der bestehenden pkg-Version ...'
    pkg add -f "$PKG" || fail 'Paket-Upgrade fehlgeschlagen; Sicherung ist erhalten.'
else
    echo 'Installiere OPNsense-Reporting-Paket ...'
    pkg add "$PKG" || fail 'Paketinstallation fehlgeschlagen; Sicherung ist erhalten.'
fi
# The corrected package does not require a pkg-recorded librespeed-cli.
# Its pre-install hook validates the already verified vendor binary.
# Package postinstall also configures cron and clears menu/ACL caches.
# Restart PHP-FPM/GUI to invalidate OPCache of the previously compiled Volt view.
# This is done after pkg completes (not inside a pkg hook), to avoid disrupting
# WebGUI-driven package operations. Installer is intended for SSH/console use.
if command -v configctl >/dev/null 2>&1; then
    echo 'Starte WebGUI neu, damit keine alte Speedtest-Seitenvorlage angezeigt wird ...'
    configctl webgui restart || echo 'WARNUNG: WebGUI nicht automatisch neu gestartet. Bitte configctl webgui restart manuell ausfuehren.' >&2
fi
[ -f /usr/local/opnsense/speedtest-csv-dashboard/status.sh ] || fail 'Paketdateien nicht vorhanden'
sh /usr/local/opnsense/speedtest-csv-dashboard/configure-cron.sh --status || fail 'Cron-Status nicht lesbar.'
sh /usr/local/opnsense/speedtest-csv-dashboard/status.sh
printf '%s\n' 'Installiert. WebGUI neu anmelden: Berichterstattung > Speedtest.'
printf '%s\n' 'Hinweis: Vorhandene OPNsense-GUI-Cronjobs werden NICHT entfernt oder verdoppelt.'
