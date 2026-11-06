#!/bin/bash
# Publish a static folder from the repo's sites/ as the whole web root of a site that has no CMS
# (a blank or static site). Backs up the current root first; vhosts, PHP pool and SSL are untouched.
#   site-deploy.sh <domain> <source folder in sites/>
# Refuses a root that holds PHP (WordPress sites use live-deploy.sh instead).
set -euo pipefail
D="$1"; SRC="/root/migration/sites/$2"
U="s_$(echo "$D" | tr '.-' '__' | cut -c1-28)"; R="/home/$U/public_html"
test -f "$SRC/index.html" || { echo "STOP: $SRC/index.html missing"; exit 1; }
test -d "$R" || { echo "STOP: $R missing (site not set up)"; exit 1; }
if [ -f "$R/wp-config.php" ] || ls "$R"/*.php >/dev/null 2>&1; then echo "STOP: $R has PHP/WordPress; use live-deploy.sh"; exit 1; fi
TS=$(date +%Y%m%d-%H%M%S); BK="/root/backups/$D-$TS"; mkdir -p "$BK"; cp -a "$R/." "$BK/"
echo "Backup: $BK ($(find "$BK" -type f | wc -l) files)"; echo "$BK" > "/root/backups/$D-latest"
rsync -a --delete --exclude .well-known "$SRC"/ "$R"/
chown -R "$U:$U" "$R"; find "$R" -type d -exec chmod 755 {} + ; find "$R" -type f -exec chmod 644 {} +
echo "Published $SRC -> $R ($(find "$R" -type f | wc -l) files, $(du -sh "$R" | cut -f1))"
for p in / /style.css /main.js /favicon.ico; do
  echo "https://$D$p -> $(curl -s --max-time 15 -o /dev/null -w '%{http_code}' --resolve "$D:443:127.0.0.1" "https://$D$p")"
done
echo "http://www.$D/ -> $(curl -s --max-time 15 -o /dev/null -w '%{http_code} %{redirect_url}' --resolve "www.$D:80:127.0.0.1" "http://www.$D/")"
