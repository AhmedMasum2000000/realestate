#!/bin/bash
# Set up one site on the VPS from the Namecheap cPanel backup in /root/migration/namecheap.
# Works for the account's main domain (web root homedir/public_html) as well as addon domains
# (homedir/<domain>). The database is found from the site's own wp-config.php. Does not touch DNS,
# so nothing changes for visitors until the domain is pointed here. Safe to rerun.
#   setup-from-backup.sh <domain> [check]     "check" only reports what would be used
set -uo pipefail
D=$1; MODE=${2:-}
N=/root/migration/namecheap; X=$N/extracted; APACHE=/usr/local/apps/apache2
T=$(ls -t $N/*.tar.gz 2>/dev/null | head -1); [ -n "$T" ] || { echo "No backup tarball in $N"; exit 1; }
echo "Backup: $T ($(du -h "$T" | cut -f1), made $(date -r "$T" '+%Y-%m-%d %H:%M'))"
if [ ! -d "$X" ] || [ "$T" -nt "$X" ]; then
  echo "Unpacking the newest backup"; rm -rf "$X.new"; mkdir -p "$X.new"; tar xzf "$T" -C "$X.new" --strip-components=1 && { rm -rf "$X"; mv "$X.new" "$X"; }
fi
MAIN=$(grep -E '^main_domain:' $X/userdata/main | awk '{print $2}')
if [ "$D" = "$MAIN" ]; then REL=homedir/public_html; else REL=homedir/$D; fi
SRC=$X/$REL
if [ ! -d "$SRC" ]; then
  # Not in the unpacked copy: pull just that folder out of the tarball (an earlier unpack may have skipped it)
  TOP=$(tar tzf "$T" | head -1 | cut -d/ -f1)
  echo "Extracting $TOP/$REL from the tarball"; tar xzf "$T" -C "$X" --strip-components=1 "$TOP/$REL" 2>&1 | tail -2
fi
if [ ! -d "$SRC" ]; then
  echo "No web root for $D in the backup ($SRC). homedir holds:"; ls -la "$X/homedir" | head -30
  echo "Entries in the tarball mentioning public_html: $(tar tzf "$T" | grep -c 'homedir/public_html')"; exit 1
fi
echo "Web root: $SRC ($(find "$SRC" -type f | wc -l) files, $(du -sh "$SRC" | cut -f1), newest file $(find "$SRC" -type f -printf '%TY-%Tm-%Td\n' | sort | tail -1))"
DUMP=""
if [ -f "$SRC/wp-config.php" ]; then
  DB=$(grep -oE "define\(\s*'DB_NAME'\s*,\s*'[^']+'" "$SRC/wp-config.php" | sed "s/.*'\([^']*\)'$/\1/")
  DUMP=$X/mysql/$DB.sql; [ -f "$DUMP" ] && echo "Database: $DB ($(du -h "$DUMP" | cut -f1))" || { echo "Database dump $DUMP missing"; exit 1; }
else echo "Not WordPress (no wp-config.php): files only"; fi
[ "$MODE" = check ] && { echo "Check only, nothing changed."; exit 0; }
bash /root/migration/vps/setup-site.sh "$D" "$SRC" "$DUMP" 2>&1 | tail -4
bash /root/migration/vps/php-service.sh >/dev/null 2>&1
$APACHE/bin/apachectl -t 2>/tmp/apache-test.txt && $APACHE/bin/apachectl -k graceful || cat /tmp/apache-test.txt
sleep 2
r=$(curl -sk -m 30 -o /tmp/page.html -w "%{http_code} %{redirect_url}" --resolve "$D:443:127.0.0.1" "https://$D/")
t=$(grep -oi "<title>[^<]*" /tmp/page.html 2>/dev/null | head -1 | sed 's/<title>//I' | cut -c1-70); rm -f /tmp/page.html
echo "Local test https://$D/ -> $r ${t:+“$t”}"
echo "Next: point $D's DNS (A @ and www) at 187.127.141.173, then ssl-site.sh $D (or auto-ssl.sh $D to do it automatically)."
