#!/bin/sh
# Install/check LibreSpeed on first-time pkg installations.
# No nested pkg operations; use verified official upstream binary only.
set -eu
umask 077
case "$(opnsense-version 2>/dev/null || true)" in *26.7.*) ;; *)
    echo 'os-speedtest-csv-reporting: Nur OPNsense 26.7.x (amd64) unterstuetzt.' >&2
    exit 1;;
esac
[ "$(uname -m)" = 'amd64' ] || { echo 'Nur amd64' >&2; exit 1; }
command -v fetch >/dev/null 2>&1 || { echo 'FreeBSD fetch fehlt' >&2; exit 1; }
command -v sha256 >/dev/null 2>&1 || { echo 'FreeBSD sha256 fehlt' >&2; exit 1; }
command -v tar >/dev/null 2>&1 || { echo 'tar fehlt' >&2; exit 1; }
command -v install >/dev/null 2>&1 || { echo 'install fehlt' >&2; exit 1; }

BIN=/usr/local/bin/librespeed-cli
URL=https://github.com/librespeed/speedtest-cli/releases/download/v1.0.14/librespeed-cli_1.0.14_freebsd_amd64.tar.gz
SHA=29c645056f4bb6f4472c694d8873db083894cd816b61aca9975c6859d252630d
if [ -x "$BIN" ] && [ ! -L "$BIN" ]; then
    "$BIN" --version 2>&1 | grep -qi librespeed || { echo 'Bestehende CLI ist nicht LibreSpeed' >&2; exit 1; }
    exit 0
fi
[ ! -e "$BIN" ] && [ ! -L "$BIN" ] || { echo 'Konflikt am LibreSpeed CLI-Pfad' >&2; exit 1; }
echo 'LibreSpeed CLI fehlt: lade offizielles Release v1.0.14 mit SHA-256-Pruefung ...'
TMP=$(mktemp -d /tmp/librespeed-preinstall.XXXXXXXX) || exit 1
trap 'rm -rf "$TMP"' EXIT HUP INT TERM
fetch -q -o "$TMP/upstream.tar.gz" "$URL" || { echo 'LibreSpeed-Download fehlgeschlagen; Internet/DNS pruefen.' >&2; exit 1; }
[ "$(sha256 -q "$TMP/upstream.tar.gz")" = "$SHA" ] || { echo 'LibreSpeed SHA-256 stimmt nicht; Installation abgebrochen.' >&2; exit 1; }
mkdir "$TMP/extracted"
tar -xzf "$TMP/upstream.tar.gz" -C "$TMP/extracted" || exit 1
FOUND=
for candidate in "$TMP/extracted/librespeed-cli" "$TMP/extracted/speedtest-cli"; do
    if [ -f "$candidate" ] && [ ! -L "$candidate" ]; then FOUND=$candidate; break; fi
done
[ -n "$FOUND" ] || { echo 'Unerwartetes LibreSpeed-Archivlayout' >&2; exit 1; }
install -m 0755 "$FOUND" "$BIN" || exit 1
"$BIN" --version 2>&1 | grep -qi librespeed || { rm -f "$BIN"; echo 'LibreSpeed CLI Validierung fehlgeschlagen' >&2; exit 1; }
echo 'LibreSpeed CLI installiert.'
