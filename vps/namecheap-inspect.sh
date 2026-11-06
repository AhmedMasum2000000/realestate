#!/bin/bash
# Read-only: unpack the Namecheap cPanel backup (once) and show each domain's web root and database settings.
set -uo pipefail
N=/root/migration/namecheap; X=$N/extracted
if [ ! -d "$X" ]; then mkdir -p $X && tar xzf $N/*.tar.gz -C $X --strip-components=1; fi
echo "== userdata"; for f in $X/userdata/*; do case "$f" in *.cache|*_SSL|*main) continue;; esac; echo "$(basename $f): $(grep -E '^(documentroot|servername):' $f | tr '\n' ' ')"; done
echo "== main"; grep -A3 -E "main_domain|addon_domains" $X/userdata/main 2>/dev/null | head -20
echo "== databases"; ls -la $X/mysql/*.sql | awk '{print $5, $9}'
echo "== config files"
for d in $X/homedir/public_html $X/homedir/*.com; do
  [ -d "$d" ] || continue; echo "-- $d"
  [ -f $d/wp-config.php ] && grep -E "DB_(NAME|USER|HOST)" $d/wp-config.php | sed -E "s/(DB_PASSWORD).*/\1 .../"
  [ -f $d/.env ] && grep -E "^(APP_URL|DB_CONNECTION|DB_HOST|DB_DATABASE|DB_USERNAME)=" $d/.env
  [ -f $d/application/config/database.php ] && grep -E "'(hostname|database|username)'" $d/application/config/database.php
  ls $d | head -12 | tr '\n' ' '; echo
done
du -sh $X/homedir/* 2>/dev/null | sort -rh | head -12
