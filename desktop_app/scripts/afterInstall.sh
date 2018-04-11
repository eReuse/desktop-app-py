#!/usr/bin/env bash

INSTALL_DIR="/dir/to/install/project"

echo "[Unit]
Description=Start DesktopApp service
After=multi-user.target

[Service]
Type=simple
ExecStart=/usr/local/bin/desktop-app

[Install]
WantedBy=multi-user.target
" | tee /etc/systemd/system/desktop-app.service

install -m 0755 ${INSTALL_DIR}/resources/desktop-app /usr/local/sbin