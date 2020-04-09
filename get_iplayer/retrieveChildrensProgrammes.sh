#!/bin/bash

#Run from cron so must not assume environment
HOME="/home/pi"

## grab each program with subtitles
/bin/cat $HOME/BluetoothMusicPlayer/get_iplayer/programs | /usr/bin/xargs $HOME/get_iplayer/get_iplayer --type=radio --channel="BBC Radio 2" -g --radiomode=good --output "$HOME/Radio_Uncompressed/tmp" $@


