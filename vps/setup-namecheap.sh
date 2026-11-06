#!/bin/bash
# Set up the Namecheap cPanel sites on the VPS from the unpacked backup, then test them locally.
#   setup-namecheap.sh domain1 domain2 ...
set -uo pipefail
X=/root/migration/namecheap/extracted; APACHE=/usr/local/apps/apache2
declare -A DUMP=( [moveinthailand.com]=pattuzhi_wp332 [secondhomethailand.com]=pattuzhi_wp379 [microgigger.com]=pattuzhi_microgiggerdb [thaihomespro.com]=pattuzhi_pattuzhi_thaihomespro_pro )
echo "| Domain | Setup | Local test (https, not live) |"; echo "|---|---|---|"
declare -A RES
for d in "$@"; do
  src=$X/homedir/$d
  [ -d "$src" ] || { RES[$d]="no copy found"; continue; }
  dump=""; [ -n "${DUMP[$d]:-}" ] && dump=$X/mysql/${DUMP[$d]}.sql
  out=$(bash /root/migration/vps/setup-site.sh "$d" "$src" "$dump" 2>&1 | tail -3 | tr '\n' ' ')
  RES[$d]=$(echo "$out" | sed 's/.*SETUP [^|]*| //')
done
bash /root/migration/vps/php-service.sh >/dev/null
$APACHE/bin/apachectl -t 2>/tmp/apache-test.txt && $APACHE/bin/apachectl -k graceful || cat /tmp/apache-test.txt
sleep 2
for d in "$@"; do
  r=$(curl -sk -m 30 -o /tmp/page.html -w "%{http_code} %{redirect_url}" --resolve "$d:443:127.0.0.1" "https://$d/")
  t=$(grep -oi "<title>[^<]*" /tmp/page.html 2>/dev/null | head -1 | sed 's/<title>//I' | cut -c1-60)
  echo "| $d | ${RES[$d]} | $r ${t:+“$t”} |"
done
df -h / | tail -1
