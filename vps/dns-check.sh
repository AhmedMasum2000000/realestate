#!/bin/bash
# Read-only: what public DNS returns for each name (A records, via 1.1.1.1 and 8.8.8.8).
for n in "$@"; do echo "== $n: $(dig +short A $n @1.1.1.1 | tr '\n' ' ') / $(dig +short A $n @8.8.8.8 | tr '\n' ' ')"; done
