#!/bin/bash
# Read-only: print a WordPress site's name, pages (text only), menus, contact details and the
# largest images in uploads, so a new design can be filled with the site's own content.
# Usage: wp-content-dump.sh <domain>
set -u
D="${1:?domain}"
U="s_$(echo "$D" | tr '.-' '__' | cut -c1-28)"
R="/home/$U/public_html"
CFG="$R/wp-config.php"
test -f "$CFG" || { echo "No wp-config.php in $R"; exit 1; }

val() { grep -E "define\(\s*['\"]$1['\"]" "$CFG" | head -1 | sed -E "s/.*define\(\s*['\"]$1['\"]\s*,\s*['\"]([^'\"]*)['\"].*/\1/"; }
DB=$(val DB_NAME); DU=$(val DB_USER); DP=$(val DB_PASSWORD)
PFX=$(grep -E '^\s*\$table_prefix' "$CFG" | sed -E "s/.*['\"]([^'\"]+)['\"].*/\1/")
# Root socket access first (read-only queries); fall back to the site's own user.
if mysql -N -B -e "SELECT 1" "$DB" >/dev/null 2>&1; then Q() { mysql -N -B -e "$1" "$DB"; }
else Q() { MYSQL_PWD="$DP" mysql -u"$DU" -h 127.0.0.1 "$DB" -N -B -e "$1"; }; fi

echo "== site"
Q "SELECT option_name, option_value FROM ${PFX}options WHERE option_name IN ('blogname','blogdescription','siteurl','page_on_front','template','stylesheet','admin_email')" | sed 's/admin_email.*/admin_email (hidden)/'

echo "== pages and posts (published)"
Q "SELECT ID, post_type, post_title, post_name FROM ${PFX}posts WHERE post_status='publish' AND post_type IN ('page','post') ORDER BY post_type, menu_order, ID"

echo "== menus"
Q "SELECT p.post_title, pm.meta_value FROM ${PFX}posts p JOIN ${PFX}postmeta pm ON pm.post_id=p.ID AND pm.meta_key='_menu_item_object_id' WHERE p.post_type='nav_menu_item' ORDER BY p.menu_order" | head -40

FRONT=$(Q "SELECT option_value FROM ${PFX}options WHERE option_name='page_on_front'")
for ID in $FRONT $(Q "SELECT ID FROM ${PFX}posts WHERE post_status='publish' AND post_type='page' ORDER BY menu_order, ID LIMIT 12"); do
  echo "== text of page $ID"
  Q "SELECT post_content FROM ${PFX}posts WHERE ID=$ID" \
    | sed -E 's/\\n/\n/g; s/<(script|style)[^>]*>.*<\/(script|style)>//g; s/<[^>]+>/ /g; s/\[[^]]*\]/ /g; s/&nbsp;/ /g; s/&amp;/\&/g' \
    | tr -s ' \t' ' ' | grep -vE '^\s*$' | head -120
  # Elementor stores page text in postmeta
  Q "SELECT meta_value FROM ${PFX}postmeta WHERE post_id=$ID AND meta_key='_elementor_data'" \
    | grep -oE '"(title|editor|description|text|heading|button_text|tab_title|testimonial_content|inner_text)":"[^"]{2,600}"' \
    | sed -E 's/\\u([0-9a-f]{4})/ /g; s/\\n/ /g; s/\\\//\//g; s/<[^>]+>/ /g' | head -150
done

echo "== phone, email, address hints"
grep -rhoE '(\+?880[ -]?1[0-9 -]{8,12}|01[3-9][0-9]{2}[ -]?[0-9]{6})' "$R/wp-content/themes" 2>/dev/null | sort | uniq -c | sort -rn | head
Q "SELECT post_content FROM ${PFX}posts WHERE post_status='publish'" | grep -oE '(\+?880[ -]?1[0-9 -]{8,12}|01[3-9][0-9]{2}[ -]?[0-9]{6}|[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[a-z]{2,})' | sort | uniq -c | sort -rn | head
Q "SELECT meta_value FROM ${PFX}postmeta WHERE meta_key='_elementor_data'" | grep -oE '(\+?880[ -]?1[0-9 -]{8,12}|01[3-9][0-9]{2}[ -]?[0-9]{6}|[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[a-z]{2,})' | sort | uniq -c | sort -rn | head

echo "== largest images in uploads"
find "$R/wp-content/uploads" -type f \( -iname '*.jpg' -o -iname '*.jpeg' -o -iname '*.png' -o -iname '*.webp' \) \
  ! -regex '.*-[0-9]+x[0-9]+\.[a-zA-Z]+$' -printf '%s %p\n' 2>/dev/null | sort -rn | head -60 | sed "s#$R#https://$D#"
echo "== logo candidates"
find "$R/wp-content/uploads" -type f -iname '*logo*' -printf '%s %p\n' 2>/dev/null | sort -rn | head -10 | sed "s#$R#https://$D#"
echo "== videos"
find "$R/wp-content/uploads" -type f \( -iname '*.mp4' -o -iname '*.webm' \) -printf '%s %p\n' 2>/dev/null | sort -rn | head -10 | sed "s#$R#https://$D#"
