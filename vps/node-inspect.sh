#!/bin/bash
# Read-only: how a copied Node.js app is built and started.
d=$1; B=/root/migration/hostinger-a/$d/files
echo "== tree"; ls -la $B; ls -la $B/public_html 2>/dev/null | head -30
for p in $B $B/public_html $B/nodejs $B/app; do
  [ -f $p/package.json ] || continue
  echo "== package.json in $p"; cat $p/package.json | head -60
  echo "== .htaccess"; cat $p/.htaccess 2>/dev/null | head -20
  echo "== env keys"; for f in $p/.env $p/.env.production $p/.env.local; do [ -f $f ] && echo "$f: $(sed -n 's/=.*//p' $f | tr '\n' ' ')"; done
  echo "== build dirs"; ls -d $p/.next $p/dist $p/build $p/server.js $p/app.js $p/index.js $p/node_modules 2>/dev/null
done
find $B -maxdepth 3 -name package.json -not -path "*/node_modules/*" | head
echo "== node on VPS: $(command -v node && node -v)"
