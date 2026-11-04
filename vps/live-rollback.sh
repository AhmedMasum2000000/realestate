#!/bin/bash
# Undo live-deploy.sh: restore the backed-up files and remove the static site.
# Usage: live-rollback.sh <domain>
set -euo pipefail
D="$1"; U="s_$(echo "$D" | tr '.-' '__' | cut -c1-28)"; R="/home/$U/public_html"
BK=$(cat /root/backups/$D-latest); test -d "$BK"
DIRS=$(cat "$BK/.dirs" 2>/dev/null || echo "assets locations")
for d in $DIRS; do [ -e "$R/$d/.ledadpro-static" ] && rm -rf "$R/$d"; done
for f in index.html sitemap-ledadpro.xml llms.txt robots.txt; do rm -f "$R/$f"; done
for f in index.html .htaccess robots.txt sitemap-ledadpro.xml llms.txt; do [ -e "$BK/$f" ] && cp -a "$BK/$f" "$R/"; done
for d in $DIRS; do [ -d "$BK/$d" ] && cp -a "$BK/$d" "$R/"; done
sed -i '/# BEGIN LEDADPRO-STATIC/,/# END LEDADPRO-STATIC/d' "$R/.htaccess"
echo "Restored from $BK"; curl -s --max-time 15 -o /dev/null -w '/ -> %{http_code}\n' --resolve "$D:443:127.0.0.1" "https://$D/"
