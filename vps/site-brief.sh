#!/bin/bash
# Read-only: one row per domain with what the VPS holds for it (user, files, kind of site, vhost, certificate).
#   site-brief.sh domain1 domain2 ...
echo "| Domain | On VPS | Files | Kind | Title (local https) | Certificate |"; echo "|---|---|---|---|---|---|"
for d in "$@"; do
  slug=$(echo "$d" | tr '.-' '__' | cut -c1-28); U="s_$slug"; W=/home/$U/public_html
  if ! id "$U" >/dev/null 2>&1 || [ ! -d "$W" ]; then echo "| $d | no | | | | |"; continue; fi
  n=$(find "$W" -type f 2>/dev/null | wc -l); sz=$(du -sh "$W" 2>/dev/null | cut -f1)
  kind="static/html"; [ -f "$W/wp-config.php" ] && kind="WordPress"; ls "$W"/*.php >/dev/null 2>&1 && [ "$kind" = static/html ] && kind="PHP"
  [ "$n" -le 1 ] && grep -q "name=\"robots\" content=\"noindex\"" "$W/index.html" 2>/dev/null && kind="blank placeholder"
  vh=""; [ -f /usr/local/apps/apache2/etc/conf.d/site-$d.conf ] && vh="vhost"
  cert="none"; if [ -f /etc/letsencrypt/live/$d/fullchain.pem ]; then cert="LE until $(openssl x509 -enddate -noout -in /etc/letsencrypt/live/$d/fullchain.pem | sed 's/notAfter=//' | cut -c1-11)"; elif [ -f /etc/sites/ssl/$d.pem ]; then cert="self-signed"; fi
  r=$(curl -sk -m 15 -o /tmp/brief.html -w '%{http_code}' --resolve "$d:443:127.0.0.1" "https://$d/")
  t=$(grep -oi "<title>[^<]*" /tmp/brief.html 2>/dev/null | head -1 | sed 's/<title>//I' | cut -c1-45); rm -f /tmp/brief.html
  echo "| $d | yes ($U) $vh | $n files, $sz | $kind | $r ${t:+“$t”} | $cert |"
done
