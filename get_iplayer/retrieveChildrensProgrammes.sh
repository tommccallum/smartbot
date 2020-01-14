#!/bin/bash

#Run from cron so must not assume environment

## grab each program with subtitles
/bin/cat $HOME/get_iplayer/programs | /usr/bin/xargs $HOME/get_iplayer/get_iplayer --type=radio --channel="BBC Radio 2" -g
/bin/mv $HOME/get_iplayer/*.m4a $HOME/Radio

