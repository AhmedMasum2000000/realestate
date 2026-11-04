#!/bin/bash
# Read-only: print one file from a site's wp-content/uploads as base64 (between FILE-BEGIN and
# FILE-END) so it can be copied out through the job log. Usage: print-upload.sh <domain> <path under uploads>
set -euo pipefail
D="$1"; P="$2"; case "$P" in *..*|/*) echo "bad path"; exit 1;; esac
U="s_$(echo "$D" | tr '.-' '__' | cut -c1-28)"; F="/home/$U/public_html/wp-content/uploads/$P"
test -f "$F"; ls -la "$F"; echo FILE-BEGIN; base64 -w0 "$F"; echo; echo FILE-END
