#!/bin/bash

sudo cp pulseaudio_system.service /etc/systemd/system/
sudo chmod 644 /etc/systemd/system/pulseaudio_system.service
sudo systemctl enable pulseaudio_system.service
sudo systemctl daemon-reload
sudo systemctl restart pulseaudio_system.service
systemctl status pulseaudio_system.service
