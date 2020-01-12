#!/bin/bash

REMAINING=$( df -h | grep "/dev/root" | awk '{print $5}' | sed "s/%//" )
if [ $REMAINING -lt 5 ]
then
	echo "Diskspace running low on Raspberry pi" | /usr/bin/mailx -r "tom@tom-mccallum.com" -s "Test" termcc@gmail.com
fi
