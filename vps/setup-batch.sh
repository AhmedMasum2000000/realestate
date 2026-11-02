#!/bin/bash
# Set up a list of migrated Hostinger sites, then start PHP, reload Apache and test each one locally.
#   setup-batch.sh a|b domain1 domain2 ...
set -uo pipefail
PLAN=$1; shift
BASE=/root/migration/hostinger-$PLAN
APACHE=/usr/local/apps/apache2
echo "| Domain | Setup | Local test (https, not live) |"; echo "|---|---|---|"
declare -A RESULT
for d in "$@"; do
  src=$BASE/$d/files/public_html
  if [ ! -d "$src" ]; then RESULT[$d]="no copy found"; continue; fi
  out=$(bash /root/migration/vps/setup-site.sh "$d" "$src" "$BASE/$d/database.sql" 2>&1 | tail -3 | tr '\n' ' ')
  RESULT[$d]=$(echo "$out" | sed 's/.*SETUP [^|]*| //')
done
bash /root/migration/vps/php-service.sh >/dev/null
if $APACHE/bin/apachectl -t 2>/tmp/apache-test.txt; then $APACHE/bin/apachectl -k graceful; else echo "APACHE CONFIG ERROR:"; cat /tmp/apache-test.txt; fi
sleep 2
for d in "$@"; do
  r=$(curl -sk -m 30 -o /tmp/page.html -w "%{http_code} %{redirect_url}" --resolve "$d:443:127.0.0.1" "https://$d/")
  t=$(grep -oi "<title>[^<]*" /tmp/page.html 2>/dev/null | head -1 | sed 's/<title>//I' | cut -c1-60)
  echo "| $d | ${RESULT[$d]} | $r ${t:+“$t”} |"
done
echo; df -h / | tail -1
