#!/bin/bash

SCRIPTPATH="$( cd "$(dirname "$0")" ; pwd -P )"

while true
do
	# is there a network interface that is not the localhost
	# that we can use?
	HAS_IPV4=$( ifconfig | grep "inet " | grep -v "127.0.0.1" )
	if [ "x${HAS_IPV4}" != "x" ]
	then
		# Test ping the google nameservers
		CAN_PING=$( ping -w 3 -c 1 8.8.8.8 | grep "1 received" )
		if [ "x${CAN_PING}" != "x" ]
		then
			break
		fi
	fi
done


$SCRIPTPATH/check_for_stream.py
