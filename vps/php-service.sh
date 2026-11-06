#!/bin/bash
# One PHP-FPM service for the migrated sites (PHP 8.3), separate from Webuzo's own panel PHP.
set -e
PHPDIR=/usr/local/apps/php83
BIN=$(ls $PHPDIR/sbin/php-fpm $PHPDIR/bin/php-fpm 2>/dev/null | head -1)
cat > /etc/sites/php-fpm.conf <<CONF
[global]
pid = /run/sites-php/php-fpm.pid
error_log = /var/log/sites/php-fpm.log
include = /etc/sites/php/*.conf
CONF
cat > /etc/systemd/system/sites-php.service <<UNIT
[Unit]
Description=PHP-FPM for migrated sites
After=network.target mariadb.service
[Service]
Type=simple
RuntimeDirectory=sites-php
RuntimeDirectoryPreserve=yes
ExecStart=$BIN --nodaemonize --fpm-config /etc/sites/php-fpm.conf -c $PHPDIR/etc/php.ini
ExecReload=/bin/kill -USR2 \$MAINPID
Restart=on-failure
[Install]
WantedBy=multi-user.target
UNIT
systemctl daemon-reload
systemctl enable sites-php >/dev/null 2>&1
if systemctl is-active --quiet sites-php; then systemctl reload sites-php; else systemctl start sites-php; fi
systemctl is-active sites-php
