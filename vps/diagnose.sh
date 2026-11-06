#!/bin/bash
# Read-only: why do these sites fail locally? Shows Apache and PHP errors and the top of the web root.
for d in "$@"; do
  slug=$(echo "$d" | tr '.-' '__' | cut -c1-28)
  echo "=== $d"; curl -sk -m 20 -o /dev/null -w "https: %{http_code}\n" --resolve "$d:443:127.0.0.1" "https://$d/"
  echo "-- apache"; tail -5 /var/log/sites/$d.err 2>/dev/null
  echo "-- php"; tail -8 /home/s_$slug/logs/php-error.log 2>/dev/null
  echo "-- web root"; ls -la /home/s_$slug/public_html | head -25
  echo "-- .htaccess"; head -30 /home/s_$slug/public_html/.htaccess 2>/dev/null
done
