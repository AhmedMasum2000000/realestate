#!/bin/bash
# Read-only: list the largest photos in a site's uploads with their pixel size, to pick
# high-resolution images. Usage: img-sizes.sh <domain>
set -u
D="${1:?domain}"; U="s_$(echo "$D" | tr '.-' '__' | cut -c1-28)"; R="/home/$U/public_html/wp-content/uploads"
PHP=$(command -v php || ls /usr/local/apps/php*/bin/php 2>/dev/null | head -1)
find "$R" -type f \( -iname '*.jpg' -o -iname '*.jpeg' -o -iname '*.png' -o -iname '*.webp' \) -size +150k \
  ! -regex '.*-[0-9]+x[0-9]+\.[a-zA-Z]+$' -print0 2>/dev/null |
  xargs -0 "$PHP" -r 'foreach (array_slice($argv,1) as $f) { $s=@getimagesize($f); if ($s && $s[0] >= 1600) printf("%dx%d %dKB %s\n",$s[0],$s[1],filesize($f)/1024,$f); }' |
  sort -t x -k1 -n -r | sed "s#/home/$U/public_html#https://$D#" | head -60
