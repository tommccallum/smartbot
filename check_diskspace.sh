#!/bin/bash

EMAILADDRESS="<your_email>@noreply.com"
REMAINING=$( df -h | grep "/dev/root" | awk '{print $5}' | sed "s/%//" )
if [ $REMAINING -lt 5 ]
then
	echo "Diskspace running low on Raspberry pi" | /usr/bin/mailx -r "tom@tom-mccallum.com" -s "Test" EMAIL_ADDRESS
fi
