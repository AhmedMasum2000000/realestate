#!/bin/bash
# Set up one migrated site on the VPS. Does not touch DNS, so the site is not live after this.
#   setup-site.sh <domain> <source folder containing the site's web root> [database dump]
# Gives the site its own Linux user, PHP-FPM pool, Apache vhosts (80 + 443 with a temporary
# self-signed certificate) and, for WordPress, its own database with the credentials already
# in wp-config.php. Safe to rerun: files are synced, the database is re-imported.
set -euo pipefail
D=$1; SRC=$2; DUMP=${3:-}
SLUG=$(echo "$D" | tr '.-' '__' | cut -c1-28); U="s_$SLUG"
HOME_D=/home/$U; WEB=$HOME_D/public_html
APACHE=/usr/local/apps/apache2; PHPV=${PHPV:-83}; PHPDIR=/usr/local/apps/php$PHPV
mkdir -p /etc/sites/php /etc/sites/ssl /run/sites-php /var/log/sites

id "$U" >/dev/null 2>&1 || useradd -m -d "$HOME_D" -s /sbin/nologin "$U"
chmod 711 "$HOME_D"; mkdir -p "$WEB" "$HOME_D/tmp" "$HOME_D/logs"
rsync -a --delete "$SRC"/ "$WEB"/
chown -R "$U:$U" "$HOME_D"
find "$WEB" -type d -exec chmod 755 {} + ; find "$WEB" -type f -exec chmod 644 {} +
[ -f "$WEB/wp-config.php" ] && chmod 600 "$WEB/wp-config.php"
APUSER=$(ps -o user= -C httpd | grep -v root | sort -u | head -1); APUSER=${APUSER:-daemon}

# PHP-FPM pool, one per site, running as the site's own user.
cat > /etc/sites/php/$SLUG.conf <<POOL
[$SLUG]
user = $U
group = $U
listen = /run/sites-php/$SLUG.sock
listen.owner = $APUSER
listen.group = $APUSER
listen.mode = 0660
pm = ondemand
pm.max_children = 8
pm.process_idle_timeout = 30s
php_admin_value[upload_tmp_dir] = $HOME_D/tmp
php_admin_value[session.save_path] = $HOME_D/tmp
php_admin_value[error_log] = $HOME_D/logs/php-error.log
php_admin_value[memory_limit] = 256M
php_admin_value[upload_max_filesize] = 128M
php_admin_value[post_max_size] = 128M
php_admin_value[max_execution_time] = 120
POOL

# Database: WordPress keeps its credentials; we recreate the same database and user locally.
DBMSG="no database"
if [ -n "$DUMP" ] && [ -f "$DUMP" ] && [ -f "$WEB/wp-config.php" ]; then
  eval "$($PHPDIR/bin/php -r '
    $c=file_get_contents($argv[1]);
    foreach(["DB_NAME","DB_USER","DB_PASSWORD","DB_HOST"] as $k){
      preg_match("/define\\(\\s*[\x27\"]".$k."[\x27\"]\\s*,\\s*[\x27\"](.*?)[\x27\"]\\s*\\)/s",$c,$m);
      echo $k."=".escapeshellarg($m[1]??"")."\n";
    }' "$WEB/wp-config.php")"
  q(){ printf "%s" "$1" | sed "s/\\\\/\\\\\\\\/g; s/'/''/g"; }
  mysql -e "CREATE DATABASE IF NOT EXISTS \`$DB_NAME\` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
            CREATE USER IF NOT EXISTS '$(q "$DB_USER")'@'localhost' IDENTIFIED BY '$(q "$DB_PASSWORD")';
            ALTER USER '$(q "$DB_USER")'@'localhost' IDENTIFIED BY '$(q "$DB_PASSWORD")';
            GRANT ALL PRIVILEGES ON \`$DB_NAME\`.* TO '$(q "$DB_USER")'@'localhost'; FLUSH PRIVILEGES;"
  # Newer mysqldump starts with a "sandbox mode" line that MariaDB 10.9 rejects; drop it, and any DEFINER.
  sed -E '/^\/\*M?!999999\\- enable the sandbox mode/d; /NOTE_VERBOSITY/d; s/DEFINER=`[^`]+`@`[^`]+`//g' "$DUMP" | mysql "$DB_NAME"
  if [ "$DB_HOST" != "localhost" ]; then
    $PHPDIR/bin/php -r '$f=$argv[1];$c=file_get_contents($f);$c=preg_replace("/(define\\(\\s*[\x27\"]DB_HOST[\x27\"]\\s*,\\s*)[\x27\"].*?[\x27\"]/","\\1\x27localhost\x27",$c,1);file_put_contents($f,$c);' "$WEB/wp-config.php"
  fi
  DBMSG="database $DB_NAME ($(mysql -N -e "select count(*) from information_schema.tables where table_schema='$DB_NAME'") tables)"
fi

# Apache: port 80 now; port 443 with a temporary self-signed certificate until Let's Encrypt.
if [ ! -f /etc/sites/ssl/selfsigned.pem ]; then
  openssl req -x509 -nodes -newkey rsa:2048 -days 30 -subj "/CN=migration.local" -keyout /etc/sites/ssl/selfsigned.key -out /etc/sites/ssl/selfsigned.crt 2>/dev/null
  cat /etc/sites/ssl/selfsigned.crt /etc/sites/ssl/selfsigned.key > /etc/sites/ssl/selfsigned.pem; chmod 600 /etc/sites/ssl/selfsigned.*
fi
CERT=/etc/sites/ssl/$D.pem; [ -f "$CERT" ] || CERT=/etc/sites/ssl/selfsigned.pem
BLOCK="  ServerName $D
  ServerAlias www.$D
  DocumentRoot $WEB
  DirectoryIndex index.php index.html index.htm
  <Directory $WEB>
    Options -Indexes +FollowSymLinks
    AllowOverride All
    Require all granted
  </Directory>
  <FilesMatch \\.php\$>
    SetHandler \"proxy:unix:/run/sites-php/$SLUG.sock|fcgi://$SLUG\"
  </FilesMatch>
  ErrorLog /var/log/sites/$D.err
  CustomLog /var/log/sites/$D.log combined"
cat > $APACHE/etc/conf.d/site-$D.conf <<VH
# Migrated site $D. Managed by vps/setup-site.sh in the realestate repo.
<VirtualHost *:80>
$BLOCK
</VirtualHost>
<VirtualHost *:443>
$BLOCK
  SSLEngine on
  SSLCertificateFile $CERT
</VirtualHost>
VH
echo "SETUP $D | user $U | $DBMSG"
