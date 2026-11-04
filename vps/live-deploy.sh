#!/bin/bash
# Put the static LED AD PRO site in front of WordPress on <domain>:
#   /  -> new homepage (index.html served before index.php), every top-level folder of the
#   build (/assets/, /locations/, /services/, /pricing/, ...), sitemap, llms.txt
# Also sends http:// and www. to the one canonical https://<domain>/ address.
# WordPress stays installed; its own pages and /wp-admin keep working. Everything replaced is
# backed up first, and vps/live-rollback.sh undoes it.
# Usage: live-deploy.sh <domain> <source folder in sites/>
set -euo pipefail
D="$1"; SRC="/root/migration/sites/$2"
U="s_$(echo "$D" | tr '.-' '__' | cut -c1-28)"; R="/home/$U/public_html"
MARK=".ledadpro-static"; TS=$(date +%Y%m%d-%H%M%S); BK="/root/backups/$D-$TS"
test -f "$SRC/index.html" && test -d "$R"
DIRS=$(cd "$SRC" && find . -mindepth 1 -maxdepth 1 -type d -printf '%f\n' | sort | tr '\n' ' ')
echo "Folders: $DIRS"
# Refuse to replace folders that are not ours
for d in $DIRS; do
  if [ -e "$R/$d" ] && [ ! -e "$R/$d/$MARK" ]; then echo "STOP: $R/$d exists and was not created by this script"; exit 1; fi
done
mkdir -p "$BK"
for f in index.html .htaccess robots.txt sitemap-ledadpro.xml llms.txt favicon.ico; do [ -e "$R/$f" ] && cp -a "$R/$f" "$BK/" || true; done
for d in $DIRS; do [ -d "$R/$d" ] && cp -a "$R/$d" "$BK/" || true; done
echo "$DIRS" > "$BK/.dirs"
echo "Backup: $BK"; echo "$BK" > /root/backups/$D-latest
# Copy new files (stage, then swap each folder)
for d in $DIRS; do
  rm -rf "$R/.$d.new"; cp -r "$SRC/$d" "$R/.$d.new"; touch "$R/.$d.new/$MARK"
  rm -rf "$R/.$d.old"; [ -d "$R/$d" ] && mv "$R/$d" "$R/.$d.old"; mv "$R/.$d.new" "$R/$d"; rm -rf "$R/.$d.old"
done
cp "$SRC/index.html" "$SRC/sitemap-ledadpro.xml" "$SRC/llms.txt" "$R/"
if [ -f "$SRC/favicon.ico" ]; then cp "$SRC/favicon.ico" "$R/favicon.ico"; chown "$U:$U" "$R/favicon.ico"; chmod 644 "$R/favicon.ico"; fi
# Our .htaccess block, rewritten on every deploy and kept above WordPress' rules
HOST_RE=${D//./\\.}
REDIRECTS=$(cat "$SRC/redirects.conf" 2>/dev/null || true)  # old WordPress URLs -> new pages
BLOCK=$(cat <<EOF
# BEGIN LEDADPRO-STATIC
DirectoryIndex index.html index.php
<IfModule mod_rewrite.c>
RewriteEngine On
RewriteCond %{REQUEST_URI} !^/\.well-known/
RewriteCond %{HTTPS} off [OR]
RewriteCond %{HTTP_HOST} !^${HOST_RE}\$ [NC]
RewriteRule ^ https://${D}%{REQUEST_URI} [L,R=301]
${REDIRECTS}
</IfModule>
# END LEDADPRO-STATIC
EOF
)
touch "$R/.htaccess"
{ echo "$BLOCK"; echo; sed '/# BEGIN LEDADPRO-STATIC/,/# END LEDADPRO-STATIC/d' "$R/.htaccess" | sed '/./,$!d'; } > "$R/.htaccess.new"
mv "$R/.htaccess.new" "$R/.htaccess"
# robots.txt: keep WordPress' defaults and list the static sitemap (the WordPress one now
# answers 410 when redirects.conf is in use, so it is no longer listed)
if [ ! -e "$BK/robots.txt" ]; then
  printf 'User-agent: *\nDisallow: /wp-admin/\nAllow: /wp-admin/admin-ajax.php\n\nSitemap: https://%s/sitemap-ledadpro.xml\n' "$D" > "$R/robots.txt"
elif ! grep -q sitemap-ledadpro "$R/robots.txt"; then
  printf '\nSitemap: https://%s/sitemap-ledadpro.xml\n' "$D" >> "$R/robots.txt"
fi
[ -n "$REDIRECTS" ] && sed -i '/wp-sitemap\.xml/d' "$R/robots.txt"
for d in $DIRS; do
  chown -R "$U:$U" "$R/$d"; find "$R/$d" -type d -exec chmod 755 {} +; find "$R/$d" -type f -exec chmod 644 {} +
done
chown "$U:$U" "$R/index.html" "$R/sitemap-ledadpro.xml" "$R/llms.txt" "$R/.htaccess" "$R/robots.txt"
chmod 644 "$R/index.html" "$R/sitemap-ledadpro.xml" "$R/llms.txt" "$R/.htaccess" "$R/robots.txt"
# Check
c() { curl -s --max-time 15 -o /tmp/ldp.html -w '%{http_code}' --resolve "$D:443:127.0.0.1" "https://$D$1"; }
echo "/ -> $(c /) $(grep -o '<title>[^<]*' /tmp/ldp.html | head -1)"
for p in /locations/ /locations/gulshan/ /locations/gulshan/advertising-cost/ /pricing/ /led-screen-rental/ /about/ /clients/ /services/led-caravan/ /guides/how-to-choose-a-billboard-location/ /assets/style.css /sitemap-ledadpro.xml /robots.txt /llms.txt /wp-login.php; do echo "$p -> $(c $p)"; done
r() { curl -s --max-time 15 -o /dev/null -w '%{http_code} %{redirect_url}' --resolve "$1:$2:127.0.0.1" "$3"; }
echo "http://$D/pricing/ -> $(r "$D" 80 "http://$D/pricing/")"
echo "https://www.$D/ -> $(r "www.$D" 443 "https://www.$D/")"
echo "static pages: $(for d in $DIRS; do find "$R/$d" -name index.html; done | wc -l)"
if [ -s "$SRC/redirects.conf" ]; then
  for p in /index.php/billboard-cost-in-dhaka/ /index.php/led-advertising-truck-rental-in-bangladesh/ /index.php/mirpur-10-led-advertising-billboard/ /index.php/some-unknown-post/ /index.php/tag/ooh-bangladesh/ /index.php/2024/05/ /index.php/my-properties/ /index.php/privacy-policy/ /wp-sitemap.xml; do
    echo "old $p -> $(r "$D" 443 "https://$D$p")"
  done
fi
