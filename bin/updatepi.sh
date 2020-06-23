#!/bin/bash

LOG="/home/pi/smartbot/log/upgrade-$(date '+%Y%m%d%H%M%S').log"
date > $LOG
echo "[TASK] CLEANUP $(date '+%Y-%m-%d %H:%M:%S')" >> $LOG
sudo find /tmp -type f -mtime +7 -iname "upgrade-*" -exec sh -c 'echo {} && rm {}' \; >> $LOG 2>&1
echo "[TASK] UPDATE $(date '+%Y-%m-%d %H:%M:%S')" >> $LOG
sudo apt-get update >> $LOG 2>&1
echo "[TASK] UPGRADE $(date '+%Y-%m-%d %H:%M:%S')" >> $LOG
sudo apt-get upgrade -y >> $LOG 2>&1
echo "[TASK] AUTOREMOVE $(date '+%Y-%m-%d %H:%M:%S')" >> $LOG
sudo apt-get autoremove >> $LOG 2>&1
echo "[TASK] AUTOCLEAN $(date '+%Y-%m-%d %H:%M:%S')" >> $LOG
sudo apt-get autoclean >> $LOG 2>&1
echo "[TASK] REBOOT $(date '+%Y-%m-%d %H:%M:%S')" >> $LOG
sudo reboot


