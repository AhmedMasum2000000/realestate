#!/bin/bash
# Free Let's Encrypt certificates for sites whose DNS already points at this VPS, then switch
# their 443 vhost from the temporary certificate to the real one. Renewals run automatically.
#   ssl-site.sh domain1 domain2 ...
set -uo pipefail
IP=187.127.141.173; APACHE=/usr/local/apps/apache2
command -v certbot >/dev/null || dnf install -y -q certbot >/dev/null
mkdir -p /etc/letsencrypt/renewal-hooks/deploy
cat > /etc/letsencrypt/renewal-hooks/deploy/sites.sh <<'HOOK'
#!/bin/bash
for d in $RENEWED_DOMAINS; do [ -f /etc/sites/ssl/$d.pem ] && cat $RENEWED_LINEAGE/fullchain.pem $RENEWED_LINEAGE/privkey.pem > /etc/sites/ssl/$d.pem; done
/usr/local/apps/apache2/bin/apachectl -k graceful
HOOK
chmod +x /etc/letsencrypt/renewal-hooks/deploy/sites.sh
systemctl enable --now certbot-renew.timer >/dev/null 2>&1 || true
echo "| Domain | DNS | Certificate | https check |"; echo "|---|---|---|---|"
for d in "$@"; do
  slug=$(echo "$d" | tr '.-' '__' | cut -c1-28); web=/home/s_$slug/public_html
  names=(-d "$d"); dns="@"
  [ "$(dig +short A $d @1.1.1.1 | tail -1)" = "$IP" ] || { echo "| $d | not pointing here yet | skipped | |"; continue; }
  [ "$(dig +short A www.$d @1.1.1.1 | tail -1)" = "$IP" ] && { names+=(-d "www.$d"); dns="@ + www"; }
  if certbot certonly --webroot -w "$web" "${names[@]}" --cert-name "$d" --non-interactive --agree-tos --register-unsafely-without-email --keep-until-expiring -q; then
    cat /etc/letsencrypt/live/$d/fullchain.pem /etc/letsencrypt/live/$d/privkey.pem > /etc/sites/ssl/$d.pem; chmod 600 /etc/sites/ssl/$d.pem
    sed -i "s#SSLCertificateFile .*#SSLCertificateFile /etc/sites/ssl/$d.pem#" $APACHE/etc/conf.d/site-$d.conf
    cert="issued"
  else cert="FAILED"; fi
  echo "| $d | $dns | $cert | |" >> /tmp/ssl-rows
done
$APACHE/bin/apachectl -t 2>/dev/null && $APACHE/bin/apachectl -k graceful; sleep 2
while IFS= read -r row; do d=$(echo "$row" | cut -d'|' -f2 | xargs)
  code=$(curl -s -m 20 -o /dev/null -w "%{http_code}" --resolve "$d:443:127.0.0.1" "https://$d/")
  echo "${row% |*| } $code |"; done < /tmp/ssl-rows 2>/dev/null; rm -f /tmp/ssl-rows
