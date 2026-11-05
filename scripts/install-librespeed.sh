#!/bin/sh
# Verify and install official LibreSpeed FreeBSD amd64 release (no bundled binary).
set -eu
umask 077
BIN=/usr/local/bin/librespeed-cli
URL=https://github.com/librespeed/speedtest-cli/releases/download/v1.0.14/librespeed-cli_1.0.14_freebsd_amd64.tar.gz
SHA=29c645056f4bb6f4472c694d8873db083894cd816b61aca9975c6859d252630d
if [ -x "$BIN" ] && [ ! -L "$BIN" ]; then
  "$BIN" --version 2>&1 | grep -qi librespeed || { echo 'Existing binary is not LibreSpeed' >&2; exit 1; }
  "$BIN" --version
  exit 0
fi
[ ! -e "$BIN" ] && [ ! -L "$BIN" ] || { echo 'Conflict at LibreSpeed binary path' >&2; exit 1; }
TMP=$(mktemp -d /tmp/librespeed.XXXXXXXX)
trap 'rm -rf "$TMP"' EXIT
fetch -q -o "$TMP/upstream.tar.gz" "$URL"
[ "$(sha256 -q "$TMP/upstream.tar.gz")" = "$SHA" ] || { echo 'LibreSpeed download checksum mismatch' >&2; exit 1; }
mkdir "$TMP/extracted"
tar -xzf "$TMP/upstream.tar.gz" -C "$TMP/extracted"
# Binary name may differ; accept only documented, explicitly named paths.
FOUND=
for candidate in "$TMP/extracted/librespeed-cli" "$TMP/extracted/speedtest-cli"; do
  if [ -f "$candidate" ] && [ ! -L "$candidate" ]; then FOUND=$candidate; break; fi
done
[ -n "$FOUND" ] || { echo 'Unknown upstream archive layout; abort' >&2; ls -l "$TMP/extracted" >&2; exit 1; }
install -m 0755 "$FOUND" "$BIN"
"$BIN" --version
