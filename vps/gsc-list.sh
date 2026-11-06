#!/bin/bash
# Read-only: every domain with a site on this VPS, one per line.
for f in /usr/local/apps/apache2/etc/conf.d/site-*.conf; do
  [ -e "$f" ] || continue
  d=$(basename "$f" .conf); d=${d#site-}
  slug=$(echo "$d" | tr '.-' '__' | cut -c1-28)
  [ -d "/home/s_$slug/public_html" ] && echo "$d"
done
