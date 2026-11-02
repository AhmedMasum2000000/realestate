#!/bin/bash
# Free disk space: remove the migration copy of site files once that site is set up under /home.
# The originals are still on Hostinger, and each site's database dump is kept.
for d in "$@"; do
  for p in /root/migration/hostinger-a/$d /root/migration/hostinger-b/$d; do
    slug=$(echo "$d" | tr '.-' '__' | cut -c1-28)
    if [ -d "$p/files" ] && [ -d "/home/s_$slug/public_html" ]; then rm -rf "$p/files"; echo "removed copy of $d"; fi
  done
done
df -h / | tail -1
