#!/bin/bash

while true;
do
    if [ -e "/tmp/say.wav" ]
    then
        mplayer /tmp/say.wav
        rm -f /tmp/say.wav
    fi
    sleep 1
done
