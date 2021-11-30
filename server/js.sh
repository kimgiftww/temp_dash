echo '[Unit]
Description=Jupyter Notebook
After=network.target
After=systemd-user-sessions.service
After=network-online.target
[Service]
Type=simple
ExecStart=/home/ubuntu/tqm/server/j.sh
TimeoutSec=30
Restart=on-failure
RestartSec=10
StartLimitInterval=350
StartLimitBurst=10
[Install]
WantedBy=multi-user.target' > j.service

sudo cp j.service /etc/systemd/system/

sudo chmod 664 /etc/systemd/system/j.service
sudo chmod 744 /home/ubuntu/tqm/server/j.sh
sudo systemctl enable j