#!/bin/bash
# Put the static LED AD PRO site in front of WordPress on <domain>:
#   /  -> new homepage (index.html served before index.php), /assets/, /locations/, sitemap, llms.txt
# WordPress stays installed; its own pages and /wp-admin keep working. Everything replaced is
# backed up first, and vps/live-rollback.sh undoes it.
# Usage: live-deploy.sh <domain> <source folder in sites/>
set -euo pipefail
D="$1"; SRC="/root/migration/sites/$2"
U="s_$(echo "$D" | tr '.-' '__' | cut -c1-28)"; R="/home/$U/public_html"
MARK=".ledadpro-static"; TS=$(date +%Y%m%d-%H%M%S); BK="/root/backups/$D-$TS"
test -f "$SRC/index.html" && test -d "$R"
# Refuse to replace folders that are not ours
for d in assets locations; do
  if [ -e "$R/$d" ] && [ ! -e "$R/$d/$MARK" ]; then echo "STOP: $R/$d exists and was not created by this script"; exit 1; fi
done
mkdir -p "$BK"
for f in index.html .htaccess robots.txt sitemap-ledadpro.xml llms.txt; do [ -e "$R/$f" ] && cp -a "$R/$f" "$BK/" || true; done
for d in assets locations; do [ -d "$R/$d" ] && cp -a "$R/$d" "$BK/" || true; done
echo "Backup: $BK"; echo "$BK" > /root/backups/$D-latest
# Copy new files (stage, then swap each folder)
for d in assets locations; do
  rm -rf "$R/.$d.new"; cp -r "$SRC/$d" "$R/.$d.new"; touch "$R/.$d.new/$MARK"
  rm -rf "$R/.$d.old"; [ -d "$R/$d" ] && mv "$R/$d" "$R/.$d.old"; mv "$R/.$d.new" "$R/$d"; rm -rf "$R/.$d.old"
done
cp "$SRC/index.html" "$SRC/sitemap-ledadpro.xml" "$SRC/llms.txt" "$R/"
# Serve index.html before index.php for the homepage
if ! grep -q "BEGIN LEDADPRO-STATIC" "$R/.htaccess" 2>/dev/null; then
  { printf '# BEGIN LEDADPRO-STATIC\nDirectoryIndex index.html index.php\n# END LEDADPRO-STATIC\n\n'; cat "$R/.htaccess" 2>/dev/null || true; } > "$R/.htaccess.new" && mv "$R/.htaccess.new" "$R/.htaccess"
fi
# robots.txt: keep WordPress' defaults and list both sitemaps
if [ ! -e "$BK/robots.txt" ]; then
  printf 'User-agent: *\nDisallow: /wp-admin/\nAllow: /wp-admin/admin-ajax.php\n\nSitemap: https://%s/sitemap-ledadpro.xml\nSitemap: https://%s/wp-sitemap.xml\n' "$D" "$D" > "$R/robots.txt"
elif ! grep -q sitemap-ledadpro "$R/robots.txt"; then
  printf '\nSitemap: https://%s/sitemap-ledadpro.xml\n' "$D" >> "$R/robots.txt"
fi
chown -R "$U:$U" "$R/assets" "$R/locations" "$R/index.html" "$R/sitemap-ledadpro.xml" "$R/llms.txt" "$R/.htaccess" "$R/robots.txt"
find "$R/assets" "$R/locations" -type d -exec chmod 755 {} +; find "$R/assets" "$R/locations" -type f -exec chmod 644 {} +
chmod 644 "$R/index.html" "$R/sitemap-ledadpro.xml" "$R/llms.txt" "$R/.htaccess" "$R/robots.txt"
# Check
c() { curl -s --max-time 15 -o /tmp/ldp.html -w '%{http_code}' --resolve "$D:443:127.0.0.1" "https://$D$1"; }
echo "/ -> $(c /) $(grep -o '<title>[^<]*' /tmp/ldp.html | head -1)"
for p in /locations/ /locations/gulshan/ /locations/gulshan/advertising-cost/ /assets/style.css /sitemap-ledadpro.xml /robots.txt /llms.txt /wp-login.php; do echo "$p -> $(c $p)"; done
echo "pages: $(find "$R/locations" -name index.html | wc -l)"
