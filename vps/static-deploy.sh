#!/bin/bash
# Publish a static folder from the repo's sites/ into a site's web root as a sub-folder preview.
# Usage: static-deploy.sh <domain> <source folder in sites/> <sub-folder, e.g. v2>
# Only that sub-folder is replaced; the rest of the site is not touched.
set -euo pipefail
D="$1"; SRC="/root/migration/sites/$2"; SUB="$3"
case "$SUB" in ""|*/*|.*) echo "Bad sub-folder"; exit 1;; esac
U="s_$(echo "$D" | tr '.-' '__' | cut -c1-28)"
R="/home/$U/public_html"
test -d "$R" && test -f "$SRC/index.html"
NEW="$R/.$SUB.new"; rm -rf "$NEW"; cp -r "$SRC" "$NEW"
chown -R "$U:$U" "$NEW"; find "$NEW" -type d -exec chmod 755 {} +; find "$NEW" -type f -exec chmod 644 {} +
rm -rf "$R/.$SUB.old"; [ -d "$R/$SUB" ] && mv "$R/$SUB" "$R/.$SUB.old"; mv "$NEW" "$R/$SUB"; rm -rf "$R/.$SUB.old"
echo "Published $SRC -> $R/$SUB"; ls -la "$R/$SUB"
code=$(curl -s -o /dev/null -w '%{http_code}' --resolve "$D:443:127.0.0.1" "https://$D/$SUB/")
echo "Local check https://$D/$SUB/ -> HTTP $code"
for f in style.css main.js; do echo "$f -> $(curl -s -o /dev/null -w '%{http_code}' --resolve "$D:443:127.0.0.1" "https://$D/$SUB/$f")"; done
