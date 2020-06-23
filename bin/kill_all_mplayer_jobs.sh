#!/bin/bash

PIDS_COUNT=$( ps ax | grep "mplayer" | grep "noconsolecontrols" | grep -v "grep" | grep -v "bash" | wc -l )
PIDS=$( ps ax | grep "mplayer" | grep "noconsolecontrols" | grep -v "grep" | grep -v "bash" | awk '{print $1}' )

if [ $PIDS_COUNT -eq 0 ]
then
	echo "No mplayer instances are running."
	exit 0
fi

echo "Existing instances:"
ps ax | grep "mplayer" | grep "noconsolecontrols" | grep -v "grep" | grep -v "bash"

for pid in ${PIDS[@]}
do
	echo "Killing job $pid"
	kill -9 $pid
done

PIDS_COUNT=$( ps ax | grep "mplayer" | grep "noconsolecontrols" | grep -v "grep" | grep -v "bash" | wc -l )
if [ $PIDS_COUNT -gt 0 ]
then
	echo "Failed to kill ${PIDS_COUNT} mplayer processes"
	ps ax | grep "mplayer"
	exit 1
fi

echo "All mplayer processes have been killed."


