#!/bin/bash
# Read-only: why a public request from the VPS fails (resolver answer and curl's error).
echo "== resolv.conf: $(grep -v '^#' /etc/resolv.conf | tr '\n' ' ')"
for d in "$@"; do
  echo "== $d getent: $(getent ahosts $d | awk '{print $1}' | sort -u | tr '\n' ' ')"
  echo "== $d curl: $(curl -s -4 -m 20 -o /dev/null "https://$d/" 2>&1; curl -sS -4 -m 20 -o /dev/null "https://$d/" 2>&1 | head -2)"
done
