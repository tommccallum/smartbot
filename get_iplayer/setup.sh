#!/bin/bash

PATH="/home/pi/get_iplayer"



echo "Install dependencies"
sudo apt install libwww-perl liblwp-protocol-https-perl libmojolicious-perl libxml-libxml-perl libcgi-pm-perl
sudo apt install ffmpeg atomicparsley

cd $PATH
echo " - Pulling latest release from GitHub"
git pull
echo " - Adding preferences to configuration"
./get_iplayer --prefs-add --type="radio" --refresh-include="BBC Radio 2"
echo " - Rebuild cache"
./get_iplayer --cache-rebuild --type="radio"
echo " - Latest cache contents"
./get_iplayer --type=radio --channel="BBC Radio 2" ".*"

