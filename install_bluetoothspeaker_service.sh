#!/bin/bash

sudo cp bluetoothspeaker.service /etc/systemd/system/
sudo chmod 644 /etc/systemd/system/bluetoothspeaker.service
sudo systemctl enable bluetoothspeaker.service
sudo systemctl daemon-reload
sudo systemctl restart bluetoothspeaker.service
systemctl status bluetoothspeaker.service
