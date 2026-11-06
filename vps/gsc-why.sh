#!/bin/bash
# Read-only: why a static file in a site's web root is not served as-is.
#   gsc-why.sh domain [file]
d=$1; n=${2:-google4b543605f291f6ad.html}
slug=$(echo "$d" | tr '.-' '__' | cut -c1-28); R=/home/s_$slug/public_html
echo "== vhost"; grep -vE '^\s*#|^\s*$' /usr/local/apps/apache2/etc/conf.d/site-$d.conf | grep -iE 'DocumentRoot|Directory|Rewrite|Handler|ProxyPass|FilesMatch|SetHandler|AllowOverride|Include' | head -30
for f in "$R/.htaccess" "$R/public/.htaccess"; do echo "== $f"; [ -f "$f" ] && grep -vE '^\s*#|^\s*$' "$f" | head -40; done
echo "== files"; ls -la "$R/$n" "$R/public/$n" 2>&1; echo "content: $(cat "$R/public/$n" 2>/dev/null)"
echo "== local fetch"; curl -s -D - --max-time 15 --resolve "$d:443:127.0.0.1" "https://$d/$n" | head -12
echo "== routes mentioning html/fallback"; grep -rnsE "fallback|\{any\}|where\(.\*.|\.html" "$R/routes" 2>/dev/null | head -10
