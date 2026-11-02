#!/bin/bash
# Read-only: how the VPS serves sites today.
C=/usr/local/apps/apache2/etc
echo "== conf.d"; ls -la $C/conf.d
echo "== webuzoVH.conf (head)"; sed -n 1,80p $C/conf.d/webuzoVH.conf
echo "== webuzo.conf (head)"; sed -n 1,40p $C/conf.d/webuzo.conf
echo "== modules"; grep -v "^#" $C/conf.d/modules.cnf | grep -v "^$" | head -60
echo "== httpd.conf Listen/User/DocumentRoot"; grep -nE "^(Listen|User|Group|DocumentRoot|ServerName|LoadModule (proxy_fcgi|php|ssl|rewrite|http2|suexec|mpm))" $C/httpd.conf
echo "== listening"; ss -ltnp | grep -E ":(80|443|3306|2002|2003|2004|2005|21|25|53) " 
echo "== php-fpm"; ps -o user=,args= -C php-fpm 2>/dev/null | sort -u | head; ls /usr/local/apps/php83/etc/ /usr/local/apps/php74/etc/ 2>/dev/null; ls /usr/local/apps/php83/etc/php-fpm.d 2>/dev/null | head
echo "== php sockets"; ls -la /run/php* /var/run/php* /usr/local/apps/php83/var/run 2>/dev/null | head
echo "== php83 modules"; /usr/local/apps/php83/bin/php -m 2>/dev/null | tr '\n' ' '; echo
echo "== mariadb root access"; mysql -e "select version(), current_user();" 2>&1 | tail -2; ls /root/.my.cnf 2>/dev/null
echo "== firewall"; firewall-cmd --list-all 2>/dev/null | head -15; csf -v 2>/dev/null | head -1
echo "== certbot/acme"; which certbot acme.sh 2>/dev/null; ls /root/.acme.sh 2>/dev/null | head -3
echo "== namecheap backup layout"; tar tzf /root/migration/namecheap/*.tar.gz | awk -F/ '{print $2"/"$3}' | sort -u | head -40
echo "== namecheap mysql dumps"; tar tzf /root/migration/namecheap/*.tar.gz | grep "/mysql/" | head -20
echo "== non-WP Hostinger sites: config files mentioning DB"; for d in ledadhub.com dhakaad.com visakori.com adprobd.com; do for p in /root/migration/hostinger-*/$d/files/public_html; do [ -d $p ] && { echo "-- $d"; ls $p | head -15; grep -rlsiE "mysqli|PDO\(|DB_HOST|DB_DATABASE|database" $p --include=*.php --include=.env --include=*.json 2>/dev/null | grep -v vendor | head -5; }; done; done
