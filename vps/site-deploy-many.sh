#!/bin/bash
# Publish several static sites in one run: pairs of <domain> <source folder in sites/>.
#   site-deploy-many.sh ledadhub.com ledadhub oohbd.com oohbd ...
set -uo pipefail
while [ $# -ge 2 ]; do
  echo "== $1 <- sites/$2"; bash /root/migration/vps/site-deploy.sh "$1" "$2" || echo "FAILED: $1"; shift 2
done
