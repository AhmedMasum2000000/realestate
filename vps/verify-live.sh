#!/bin/bash
# Check each site the way visitors reach it: real public DNS, https, over IPv4 and IPv6.
echo "| Domain | IPv4 | IPv6 | www | Title |"; echo "|---|---|---|---|---|"
for d in "$@"; do
  c4=$(curl -4 -s -m 20 -o /tmp/p.html -w "%{http_code}" "https://$d/")
  c6=$(curl -6 -s -m 20 -o /dev/null -w "%{http_code}" "https://$d/" 2>/dev/null || echo "-")
  cw=$(curl -4 -s -m 20 -o /dev/null -w "%{http_code}" "https://www.$d/")
  t=$(grep -oi "<title>[^<]*" /tmp/p.html | head -1 | sed 's/<title>//I' | cut -c1-50)
  echo "| $d | $c4 | $c6 | $cw | $t |"
done
