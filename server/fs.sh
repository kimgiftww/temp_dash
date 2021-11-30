echo '[Unit]
Description=Gunicorn Flask Application
After=network.target
After=systemd-user-sessions.service
After=network-online.target

[Service]
Type=simple
ExecStart=/home/ubuntu/tqm/server/f5.sh
TimeoutSec=30
Restart=on-failure
RestartSec=5
StartLimitInterval=350
StartLimitBurst=10

[Install]
WantedBy=multi-user.target' > f5.service

sudo cp f5.service /etc/systemd/system/

sudo chmod 664 /etc/systemd/system/f5.service
sudo chmod 744 /home/ubuntu/tqm/server/f5.sh
sudo systemctl enable f5