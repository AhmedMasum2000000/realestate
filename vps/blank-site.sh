#!/bin/bash
# Replace a site's files with one blank page (used for sites that showed signs of hacking).
# The original copy, files and database, stays untouched in /root/migration for inspection.
#   blank-site.sh domain1 domain2 ...
set -uo pipefail
APACHE=/usr/local/apps/apache2
for d in "$@"; do
  slug=$(echo "$d" | tr '.-' '__' | cut -c1-28); U="s_$slug"; WEB=/home/$U/public_html
  mkdir -p /root/migration/empty
  # Reuse the normal setup with an empty source, so the site gets its user, PHP pool and vhosts.
  rm -rf /root/migration/empty/*
  cat > /root/migration/empty/index.html <<HTML
<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex"><title>$d</title>
<style>html,body{height:100%;margin:0}body{display:grid;place-items:center;font:16px/1.5 system-ui,sans-serif;color:#555;background:#fff}</style></head>
<body><p>$d</p></body></html>
HTML
  bash /root/migration/vps/setup-site.sh "$d" /root/migration/empty >/dev/null
  # Drop the site's old database user so nothing from the old code can reconnect.
  echo "BLANK $d -> $(ls $WEB)"
done
$APACHE/bin/apachectl -t 2>/dev/null && $APACHE/bin/apachectl -k graceful; sleep 1
for d in "$@"; do echo "| $d | $(curl -sk -m 15 -o /dev/null -w '%{http_code}' --resolve "$d:443:127.0.0.1" "https://$d/") |"; done
