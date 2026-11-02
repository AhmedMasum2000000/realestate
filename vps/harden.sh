#!/bin/bash
# Close the loopholes found after the migration. Safe to rerun.
set -uo pipefail
APACHE=/usr/local/apps/apache2
say(){ echo "== $*"; }

say "1. Firewall: allow only SSH, web and the Webuzo panel"
command -v firewall-cmd >/dev/null || dnf install -y -q firewalld >/dev/null
systemctl enable --now firewalld >/dev/null 2>&1
firewall-cmd -q --permanent --add-service=ssh
firewall-cmd -q --permanent --add-service=http
firewall-cmd -q --permanent --add-service=https
firewall-cmd -q --permanent --add-port=2002-2005/tcp
for s in mysql dns ftp smtp; do firewall-cmd -q --permanent --remove-service=$s 2>/dev/null; done
for p in 3306/tcp 53/tcp 53/udp 21/tcp 25/tcp; do firewall-cmd -q --permanent --remove-port=$p 2>/dev/null; done
firewall-cmd -q --reload
echo "open: $(firewall-cmd --list-services) $(firewall-cmd --list-ports)"

say "2-3. No PHP in uploads; block xmlrpc.php; basic security headers (every site)"
cat > $APACHE/etc/conf.d/zz-sites-hardening.conf <<'CONF'
# Applies to every migrated site under /home/s_*.
<DirectoryMatch "^/home/s_[^/]+/public_html/wp-content/uploads">
  <FilesMatch "\.(php|phtml|phar|php[0-9])$">
    Require all denied
  </FilesMatch>
</DirectoryMatch>
<DirectoryMatch "^/home/s_[^/]+/public_html">
  <Files "xmlrpc.php">
    Require all denied
  </Files>
  <FilesMatch "^(\.env|\.git.*|wp-config\.php\.bak|.*\.sql|composer\.(json|lock))$">
    Require all denied
  </FilesMatch>
</DirectoryMatch>
<IfModule headers_module>
  Header always set X-Content-Type-Options "nosniff"
  Header always set X-Frame-Options "SAMEORIGIN"
  Header always set Referrer-Policy "strict-origin-when-cross-origin"
</IfModule>
CONF

say "4. fail2ban for SSH"
command -v fail2ban-client >/dev/null || dnf install -y -q fail2ban >/dev/null
cat > /etc/fail2ban/jail.d/sshd.local <<'J'
[sshd]
enabled = true
backend = systemd
maxretry = 5
findtime = 10m
bantime = 1h
J
systemctl enable --now fail2ban >/dev/null 2>&1; systemctl restart fail2ban
echo "fail2ban: $(fail2ban-client status sshd 2>/dev/null | grep -o 'Currently banned:.*')"

say "5. thaihomespro.com: open installer replaced with a blank page"
bash /root/migration/vps/blank-site.sh thaihomespro.com | grep -v "^|"

say "6. Remove hacked copies, their databases, and finished migration copies"
for d in ledadhub.com transitadpro.com oohadpro.com billboardadhub.com; do
  for p in /root/migration/hostinger-a/$d /root/migration/hostinger-b/$d; do [ -d $p ] && rm -rf $p && echo "removed copy $p"; done
done
# Databases of the four suspicious sites (their blank pages need none).
mysql -N -e "select distinct db from mysql.db" | while read db; do :; done
for u in s_ledadhub_com s_transitadpro_com s_oohadpro_com s_billboardadhub_com s_thaihomespro_com; do
  find /home/$u/public_html -mindepth 1 ! -name index.html -exec rm -rf {} + 2>/dev/null
done
for dump in /root/migration/hostinger-b/billboardadhub.com/database.sql /root/migration/hostinger-b/transitadpro.com/database.sql /root/migration/hostinger-b/oohadpro.com/database.sql; do :; done
# Drop the databases the suspicious sites used, found by their imported names.
for db in $(mysql -N -e "select schema_name from information_schema.schemata where schema_name in ('u463099719_DtMFR','u463099719_YKaS2','u463099719_x7tww','pattuzhi_pattuzhi_thaihomespro_pro')"); do
  mysql -e "DROP DATABASE \`$db\`" && echo "dropped database $db"
done
# Finished sites: drop the copied files (originals remain on the old hosting); keep database dumps.
for p in /root/migration/hostinger-a/*/files /root/migration/hostinger-b/*/files; do [ -d "$p" ] && rm -rf "$p"; done
rm -rf /root/migration/namecheap/extracted/homedir /root/migration/empty
echo "remaining migration data: $(du -sh /root/migration | cut -f1)"

$APACHE/bin/apachectl -t 2>/tmp/ap.txt && $APACHE/bin/apachectl -k graceful || cat /tmp/ap.txt
say "Checks"
sleep 2
for d in marufsunny.com moveinthailand.com thaihomespro.com; do echo "$d: $(curl -s -m 20 -o /dev/null -w '%{http_code}' https://$d/ --resolve $d:443:127.0.0.1 -k)"; done
echo "xmlrpc on marufsunny.com: $(curl -sk -m 20 -o /dev/null -w '%{http_code}' https://marufsunny.com/xmlrpc.php --resolve marufsunny.com:443:127.0.0.1)"
echo "php in uploads on marufsunny.com: $(curl -sk -m 20 -o /dev/null -w '%{http_code}' https://marufsunny.com/wp-content/uploads/smile_fonts/phlox/charmap.php --resolve marufsunny.com:443:127.0.0.1)"
echo "listening publicly: $(ss -ltn | awk 'NR>1{print $4}' | grep -vE '^(127\.|\[::1\])' | sed 's/.*://' | sort -un | tr '\n' ' ')"
df -h / | tail -1
