#!/bin/bash
# Read-only: everything that shows a site was moved and is served by this VPS.
d=$1; slug=$(echo "$d" | tr '.-' '__' | cut -c1-28); U=s_$slug; W=/home/$U/public_html
db=$(sed -n "s/.*define( *['\"]DB_NAME['\"] *, *['\"]\([^'\"]*\)['\"].*/\1/p" $W/wp-config.php 2>/dev/null | head -1)
echo "FACT|Server hostname|$(hostname)"
echo "FACT|Server IP|$(hostname -I | awk '{print $1}')"
echo "FACT|Operating system|$(. /etc/os-release; echo $PRETTY_NAME)"
echo "FACT|Site Linux user|$U (uid $(id -u $U))"
echo "FACT|Web root|$W"
echo "FACT|Files|$(find $W -type f | wc -l) files, $(du -sh $W | cut -f1)"
echo "FACT|WordPress version|$(sed -n "s/^\$wp_version = '\(.*\)';/\1/p" $W/wp-includes/version.php)"
echo "FACT|Database|$db: $(mysql -N -e "select count(*) from information_schema.tables where table_schema='$db'") tables, $(mysql -N -e "select round(sum(data_length+index_length)/1024/1024,1) from information_schema.tables where table_schema='$db'") MB"
echo "FACT|Posts and pages|$(mysql -N -e "select count(*) from \`$db\`.$(mysql -N -e "select table_name from information_schema.tables where table_schema='$db' and table_name like '%\\_posts' limit 1") where post_status='publish'") published"
echo "FACT|Site URL in database|$(mysql -N -e "select option_value from \`$db\`.$(mysql -N -e "select table_name from information_schema.tables where table_schema='$db' and table_name like '%\\_options' limit 1") where option_name='siteurl'")"
echo "FACT|Apache vhost|/usr/local/apps/apache2/etc/conf.d/site-$d.conf"
echo "FACT|PHP|PHP-FPM 8.3 pool $slug ($(systemctl is-active sites-php))"
echo "FACT|Web server|Apache $(/usr/local/apps/apache2/bin/httpd -v | sed -n 's/.*Apache\/\([0-9.]*\).*/\1/p') ($(systemctl is-active httpd))"
echo "FACT|Database server|MariaDB $(mysql -N -e 'select version()' | cut -d- -f1) ($(systemctl is-active mariadb))"
echo "FACT|SSL certificate|$(openssl x509 -in /etc/letsencrypt/live/$d/fullchain.pem -noout -issuer | sed 's/.*O = //;s/, CN.*//'), serial $(openssl x509 -in /etc/letsencrypt/live/$d/fullchain.pem -noout -serial | cut -d= -f2), expires $(openssl x509 -in /etc/letsencrypt/live/$d/fullchain.pem -noout -enddate | cut -d= -f2)"
echo "FACT|Visits served today|$(grep -c "$(date +%d/%b/%Y)" /var/log/sites/$d.log) requests in the VPS access log"
echo "FACT|Firewall|$(firewall-cmd --state) (open: $(firewall-cmd --list-services | tr ' ' ','))"
