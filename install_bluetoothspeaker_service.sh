#!/bin/bash

SERVICE="bluetoothspeaker.service"
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
SERVDIR="${DIR}/systemd"
DESTDIR="/etc/systemd/system"
sudo cp $SERVDIR/$SERVICE $DESTDIR
sudo chmod 644 $DESTDIR/$SERVICE
sudo systemctl enable $SERVICE
sudo systemctl daemon-reload
sudo systemctl restart $SERVICE
systemctl status $SERVICE
