#!/usr/bin/env bash

echo "[Unit]
Description=Start WorkbenchServer service
After=multi-user.target

[Service]
Type=simple
ExecStart=/usr/local/bin/workbench-server

[Install]
WantedBy=multi-user.target
" | tee /etc/systemd/system/desktop-app.service

install -m 0755 ${SCRIPT_DIR}/resources/desktop-app /usr/local/sbin