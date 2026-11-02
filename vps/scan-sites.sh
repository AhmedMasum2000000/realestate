#!/bin/bash
# Read-only: look for common signs that a site was hacked. Prints one row per site.
#   scan-sites.sh domain1 domain2 ...
echo "| Domain | Suspicious files | Code patterns in PHP | Verdict |"; echo "|---|---|---|---|"
for d in "$@"; do
  slug=$(echo "$d" | tr '.-' '__' | cut -c1-28); w=/home/s_$slug/public_html
  [ -d "$w" ] || { echo "| $d | not set up | | |"; continue; }
  # PHP files in uploads, odd PHP at the web root, and well-known backdoor patterns.
  up=$(find "$w/wp-content/uploads" -name "*.php" -not -name "index.php" 2>/dev/null | wc -l)
  odd=$(ls "$w"/*.php 2>/dev/null | xargs -n1 basename 2>/dev/null | grep -vxE "index|wp-[a-z-]+|xmlrpc|artisan|server|configurator|cron|install|update|readme" -e '' | sed 's/\.php$//' | grep -vE "^wp-(activate|blog-header|comments-post|config|config-sample|cron|links-opml|load|login|mail|settings|signup|trackback)$|^(index|xmlrpc)$" | head -5 | tr '\n' ' ')
  pat=$(grep -rlsE --include=*.php "eval\s*\(\s*(base64_decode|gzinflate|str_rot13|gzuncompress)|assert\s*\(\s*\\\$_(POST|GET|REQUEST)|\\\$_(POST|GET|REQUEST|COOKIE)\[[^]]+\]\s*\(|preg_replace\s*\(\s*['\"]/.*/e['\"]|(\\\\x[0-9a-f]{2}){20}" "$w" 2>/dev/null | grep -v "/vendor/" | head -200 | wc -l)
  core=""; [ -f "$w/wp-load.php" ] && { [ -f "$w/wp-config.php" ] && [ -f "$w/wp-blog-header.php" ] || core="WordPress core files missing "; }
  verdict="clean"; { [ "$up" -gt 0 ] || [ -n "$odd" ] || [ "$pat" -gt 0 ] || [ -n "$core" ]; } && verdict="SUSPICIOUS"
  echo "| $d | ${core}${odd:+root: $odd }${up:+uploads php: $up} | $pat | $verdict |"
done
