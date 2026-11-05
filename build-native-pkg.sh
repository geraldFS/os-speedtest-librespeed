#!/bin/sh
# Recommended for public releases: build using FreeBSD's own pkg create.
# Run on isolated OPNsense 26.7 build/test VM, not on production firewall.
set -eu
ROOT=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
[ "$(uname -s)" = 'FreeBSD' ] || { echo 'FreeBSD/OPNsense build host required' >&2; exit 1; }
command -v pkg >/dev/null 2>&1 || exit 1
TMP=$(mktemp -d /tmp/os-speedtest-build.XXXXXXXX)
trap 'rm -rf "$TMP"' 0
mkdir -p "$TMP/stage" "$TMP/meta" "$ROOT/dist"
PLIST="$TMP/plist"
: > "$PLIST"
while IFS='|' read -r src dest; do
    [ -n "$src" ] || continue
    mkdir -p "$TMP/stage/$(dirname "${dest#/}")"
    case "$dest" in *.sh|*.py) mode=0755;; *) mode=0644;; esac
    install -m "$mode" "$ROOT/$src" "$TMP/stage/${dest#/}"
    # FreeBSD pkg-plist entries are relative to prefix /usr/local.
    printf '%s\n' "${dest#/usr/local/}" >> "$PLIST"
done < "$ROOT/manifest.txt"
# The official CLI is fetched and verified by the preinstall hook, not a hard pkg dependency.
# Vendor binaries can be installed outside the FreeBSD Ports package registry.
cat > "$TMP/meta/+MANIFEST" <<'EOF'
name: "os-speedtest-csv-reporting"
version: "0.5.4-L"
origin: "local/os-speedtest-csv-reporting"
comment: "Unofficial LibreSpeed reporting for OPNsense 26.7"
maintainer: "geraldFS"
www: "https://github.com/geraldFS/os-speedtest-librespeed"
arch: "FreeBSD:15:amd64"
prefix: "/usr/local"
licenselogic: "single"
licenses: ["MIT"]
EOF
cat > "$TMP/meta/+DESC" <<'EOF'
Unofficial OPNsense LibreSpeed Reporting: LibreSpeed CLI, dashboard and reports.
The vendor binary is NOT redistributed. The official CLI is verified and bootstrapped by the pre-install hook.
EOF
cp "$ROOT/hooks/pre-install.sh" "$TMP/meta/+PRE_INSTALL"
cp "$ROOT/hooks/post-install.sh" "$TMP/meta/+POST_INSTALL"
cp "$ROOT/hooks/pre-deinstall.sh" "$TMP/meta/+PRE_DEINSTALL"
cp "$ROOT/hooks/post-deinstall.sh" "$TMP/meta/+POST_DEINSTALL"
pkg create -m "$TMP/meta" -r "$TMP/stage" -p "$PLIST" -o "$ROOT/dist"
echo 'Native package created; smoke-test pkg add/pkg info/pkg delete on an isolated VM.'
