#!/bin/bash
# Read-only: list client/brand logo images on a WordPress site (by file name and by images
# used in logo/client carousels in page builders), with pixel sizes, so a clients page can be built.
# Usage: client-logos.sh <domain>
set -u
D="${1:?domain}"; U="s_$(echo "$D" | tr '.-' '__' | cut -c1-28)"; R="/home/$U/public_html"
CFG="$R/wp-config.php"; test -f "$CFG" || { echo "No WordPress at $R"; exit 1; }
val() { grep -E "define\(\s*['\"]$1['\"]" "$CFG" | head -1 | sed -E "s/.*define\(\s*['\"]$1['\"]\s*,\s*['\"]([^'\"]*)['\"].*/\1/"; }
DB=$(val DB_NAME); PFX=$(grep -E '^\s*\$table_prefix' "$CFG" | sed -E "s/.*['\"]([^'\"]+)['\"].*/\1/")
Q() { mysql -N -B -e "$1" "$DB"; }
echo "== pages mentioning clients"
Q "SELECT ID, post_title FROM ${PFX}posts WHERE post_status='publish' AND (post_title LIKE '%client%' OR post_content LIKE '%client%' OR post_title LIKE '%portfolio%') LIMIT 30"
echo "== images in builder data of pages that mention clients/partners/brands"
Q "SELECT meta_value FROM ${PFX}postmeta WHERE meta_key='_elementor_data' AND (meta_value LIKE '%client%' OR meta_value LIKE '%partner%' OR meta_value LIKE '%brand%')" \
  | grep -oE 'wp-content\\?/uploads\\?/[^"]+\.(png|jpe?g|webp|svg)' | sed 's#\\##g' | sort -u > /tmp/cl-builder.txt
wc -l < /tmp/cl-builder.txt
echo "== image file names that look like logos"
find "$R/wp-content/uploads" -type f \( -iname '*logo*' -o -iname '*client*' -o -iname '*brand*' \) \
  ! -regex '.*-[0-9]+x[0-9]+\.[a-zA-Z]+$' -printf 'wp-content/uploads/%P\n' 2>/dev/null | sort -u > /tmp/cl-names.txt
wc -l < /tmp/cl-names.txt
echo "== attachment titles (alt text) of builder images"
cat /tmp/cl-builder.txt /tmp/cl-names.txt | sort -u | while read -r p; do
  f="$R/$p"; [ -f "$f" ] || continue
  t=$(Q "SELECT p.post_title FROM ${PFX}posts p JOIN ${PFX}postmeta m ON m.post_id=p.ID AND m.meta_key='_wp_attached_file' WHERE m.meta_value='${p#wp-content/uploads/}' LIMIT 1")
  printf '%s\t%s\t%s\n' "$(identify -format '%wx%h' "$f" 2>/dev/null || echo ?)" "https://$D/$p" "$t"
done | head -400
