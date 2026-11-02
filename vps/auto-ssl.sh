#!/bin/bash
# Install a 10-minute timer: any domain in /etc/sites/pending-ssl whose DNS now points at this VPS
# gets its Let's Encrypt certificate automatically, then leaves the list.
#   auto-ssl.sh domain1 domain2 ...   (adds them to the list and installs/refreshes the timer)
set -uo pipefail
mkdir -p /etc/sites /usr/local/sbin/sites
cp /root/migration/vps/ssl-site.sh /usr/local/sbin/sites/ssl-site.sh
for d in "$@"; do grep -qx "$d" /etc/sites/pending-ssl 2>/dev/null || echo "$d" >> /etc/sites/pending-ssl; done
cat > /usr/local/sbin/sites/pending-ssl-check.sh <<'RUN'
#!/bin/bash
IP=187.127.141.173; LIST=/etc/sites/pending-ssl; [ -s $LIST ] || exit 0
for d in $(cat $LIST); do
  [ "$(dig +short A $d @1.1.1.1 | tail -1)" = "$IP" ] || continue
  out=$(bash /usr/local/sbin/sites/ssl-site.sh $d 2>&1)
  if echo "$out" | grep -q "| $d | .* | issued |"; then sed -i "/^$d\$/d" $LIST; echo "$(date -Is) $d live with https" >> /var/log/sites/auto-ssl.log; fi
done
RUN
chmod +x /usr/local/sbin/sites/*.sh
cat > /etc/systemd/system/sites-pending-ssl.service <<'U'
[Unit]
Description=Issue SSL for migrated sites once their DNS points here
[Service]
Type=oneshot
ExecStart=/usr/local/sbin/sites/pending-ssl-check.sh
U
cat > /etc/systemd/system/sites-pending-ssl.timer <<'U'
[Unit]
Description=Check pending SSL every 10 minutes
[Timer]
OnBootSec=2min
OnUnitActiveSec=10min
[Install]
WantedBy=timers.target
U
systemctl daemon-reload; systemctl enable --now sites-pending-ssl.timer >/dev/null 2>&1
echo "== waiting for DNS: $(tr '\n' ' ' < /etc/sites/pending-ssl)"
echo "== timer: $(systemctl is-active sites-pending-ssl.timer)"
systemctl start sites-pending-ssl.service; echo "== first check done; still waiting: $(tr '\n' ' ' < /etc/sites/pending-ssl)"
