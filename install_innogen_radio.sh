#!/bin/bash

sudo cp innogen_radio.service /etc/systemd/system/
sudo chmod 644 /etc/systemd/system/innogen_radio.service
sudo systemctl enable innogen_radio.service
sudo systemctl daemon-reload
sudo systemctl restart innogen_radio.service
systemctl status innogen_radio.service
