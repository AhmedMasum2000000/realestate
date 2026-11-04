#!/bin/bash
# Put Google's Search Console verification files in each site's web root.
# Input: /root/migration/gsc-files/<domain>/google<hex>.html (made by bin/gsc-vps prepare).
# The files stay in place: Google re-checks them to keep the site verified.
set -euo pipefail
IN=/root/migration/gsc-files
for dir in "$IN"/*/; do
  [ -d "$dir" ] || continue
  d=$(basename "$dir")
  slug=$(echo "$d" | tr '.-' '__' | cut -c1-28); U="s_$slug"; R="/home/$U/public_html"
  [ -d "$R" ] || { echo "$d: no web root, skipped"; continue; }
  # Where files are really served from: the web root, the vhost's DocumentRoot,
  # and public/ for Laravel-style apps whose .htaccess sends everything there.
  targets=("$R")
  dr=$(sed -n 's/^[[:space:]]*DocumentRoot[[:space:]]\+"\{0,1\}\([^"]*\)"\{0,1\}.*/\1/p' \
       "/usr/local/apps/apache2/etc/conf.d/site-$d.conf" 2>/dev/null | head -1)
  [ -n "$dr" ] && [ -d "$dr" ] && [ "${dr%/}" != "$R" ] && targets+=("${dr%/}")
  # Laravel sites copied from Hostinger forward requests to public/, but their root
  # .htaccess mangles requests for files that exist in the root (they end in
  # server.php, which answers an empty page). There the file must be in public/ only.
  laravel=""
  if [ -d "$R/public" ] && grep -qs 'public/' "$R/.htaccess"; then laravel=1; targets=("$R/public"); fi
  for f in "$dir"google*.html; do
    [ -e "$f" ] || continue
    n=$(basename "$f")
    [[ "$n" =~ ^google[0-9a-f]+\.html$ ]] || { echo "$d: bad file name $n, skipped"; continue; }
    [ -n "$laravel" ] && rm -f "$R/$n"
    for t in "${targets[@]}"; do install -m 644 -o "$U" -g "$U" "$f" "$t/$n"; done
    echo "$d: placed in ${targets[*]}"
    code=$(curl -s --max-time 15 -o /dev/null -w '%{http_code}' --resolve "$d:443:127.0.0.1" "https://$d/$n" || true)
    echo "$d: $n placed ($code)"
  done
done
rm -rf "$IN"
