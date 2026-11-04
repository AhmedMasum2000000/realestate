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
  for f in "$dir"google*.html; do
    [ -e "$f" ] || continue
    n=$(basename "$f")
    [[ "$n" =~ ^google[0-9a-f]+\.html$ ]] || { echo "$d: bad file name $n, skipped"; continue; }
    install -m 644 -o "$U" -g "$U" "$f" "$R/$n"
    code=$(curl -s --max-time 15 -o /dev/null -w '%{http_code}' --resolve "$d:443:127.0.0.1" "https://$d/$n" || true)
    echo "$d: $n placed ($code)"
  done
done
rm -rf "$IN"
