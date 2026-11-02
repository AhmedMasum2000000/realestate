#!/bin/bash
# Read-only: how long each page takes, from the VPS (direct, local) and through the public IPv4 address.
for d in "$@"; do
  for i in 1 2; do
    l=$(curl -sk -m 60 -o /dev/null -w "%{http_code} %{time_total}s" --resolve "$d:443:127.0.0.1" "https://$d/")
    p=$(curl -s -4 -m 60 -o /dev/null -w "%{http_code} %{time_total}s" "https://$d/")
    echo "== $d try $i: local $l | public-v4 $p"
  done
done
