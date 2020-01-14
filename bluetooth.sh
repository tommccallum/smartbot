#!/bin/bash

# Check that Pulseaudio is loaded, if not start it
HOMEDIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
BLUETOOTH_DEVICE=$( cat "${HOMEDIR}/Bluetooth_Speaker.txt" )
EXPECTED_PULSE_APP="pulseaudio"
HELLOWORLD="${HOMEDIR}/Tardis-sound.wav"
SYSTEMCTL=$1

echo "User: ${USER}"

if [ ! -e "${HELLOWORLD}" ]
then
	echo "Could not find ${HELLOWORLD}"
	exit 10
fi

if [ "x${BLUETOOTH_DEVICE}" == "" ]
then
	echo "Could not find bluetooth speaker device address"
	exit 100
fi
echo "[OK] Bluetooth device is ${BLUETOOTH_DEVICE}"


# begin an infinite loop where we check if our device has lost
# connection for some reason
while true
do

	CONN=$( hcitool con | grep "${BLUETOOTH_DEVICE}" )
	if [ "x$CONN" == "x" ]
	then
		echo "No connection found, attempting to reconnect..."

		PULSE_PID=$( ps aux | grep "$EXPECTED_PULSE_APP" | awk '{print $2}')
		if [ "x$PULSE_PID" == "x" ]
		then
			echo "Attempting to start Pulseaudio..."
			pulseaudio --start
			PULSE_PID=$( ps aux | grep "$EXPECTED_PULSE_APP" | awk '{print $2}')
			if [ "x$PULSE_PID" == "x" ]
			then
		        	echo "[ERROR] Pulseaudio is not running!"
	        		exit 1
			else
				echo "Pulseaudio is now running on pid $PULSE_PID"
			fi
		fi

		echo "Attempting to scan for bluetooth device"
		$HOMEDIR/bluetooth_speaker.expect "${BLUETOOTH_DEVICE}"
		if [ $? != 0 ]
		then
			# if was not successful then loop
			sleep 5
			continue
		fi

		
		PULSE_SINK=$( pactl list sinks short | grep "module-bluez5-device.c" | awk '{print $1}' )
		if [ "x$PULSE_SINK" == "x" ]
		then
			echo "[ERROR] Pulseaudio has not picked up a bluetooth device!"
			pactl list sinks short
			exit 2
		else
			echo "[OK] Detected pulseaudio bluetooth device (${PULSE_SINK})"
		fi

		A2DP=$( pactl list | grep -A 18 "bluez" | grep "Active Profile" | awk '{print $3}' )
		if [ "x${A2DP}" != "xa2dp_sink" ]
		then
			CARD=$( pactl list | grep -B 2 bluez | grep Card | sed "s/Card #//" )
			echo "Attempting to set card profile on card #${CARD}"
			pactl set-card-profile ${CARD} a2dp_sink
			A2DP=$( pactl list sinks short | grep "module-bluez5-device.c" | grep "a2dp_sink" | awk '{print $1}' )
			if [ "x$A2DP" == "x" ]
			then
				echo "[ERROR] Failed to set speaker to a2dp_sink profile."
				exit 3
			fi
		fi

		A2DP=$( pactl list sinks short | grep "module-bluez5-device.c" | grep "a2dp_sink" | awk '{print $1}' )
		pactl set-default-sink $A2DP
		if [ $? == 0 ]
		then
			echo "[OK] Detected a2dp bluetooth device, attempting to play test sound"
                        timeout 15 aplay "${HELLOWORLD}"
                        if [ $? != 0 ]
                        then
	                        echo "[ERROR] aplay failed to complete"
                                exit 4
                        else
                                echo "[OK] aplay completed"
                        fi
		fi
	fi

	# if a bluetooth device is listed at all
	#	then check its set up properly
	PULSE_SINK=$( pactl list sinks short | grep "module-bluez5-device.c" | awk '{print $1}' )
	if [ "x$PULSE_SINK" != "x" ]
	then
		#pactl info | grep "Default" | grep -i "sink" | grep "bluez" 
		SINK=$( pactl info | grep "Default" | grep -i "sink" | grep "bluez" )
		if [ "x$SINK" != "x" ]
		then

			A2DP=$( pactl list | grep -A 18 "bluez" | grep "Active Profile" | awk '{print $3}' )
	                if [ "x${A2DP}" != "xa2dp_sink" ]
                	then
				CARD=$( pactl list | grep -B 2 bluez | grep Card | sed "s/Card #//" )
				echo "Attempting to select a2dp_sink profile for card ${CARD}"
                        	pactl set-card-profile ${CARD} a2dp_sink
				pactl list sinks short | grep "module-bluez5-device.c" | grep "a2dp_sink" 

	                        A2DP=$( pactl list sinks short | grep "module-bluez5-device.c" | grep "a2dp_sink" | awk '{print $1}' )
        	                if [ "x$A2DP" == "x" ]
                	        then
                        	        echo "[ERROR] Failed to set speaker to a2dp_sink profile."
                                	exit 3
	                        fi
        	   
                		pactl set-default-sink $A2DP
	                	if [ $? == 0 ]
	        	        then
        	        	        echo "[OK] Detected a2dp bluetooth device, attempting to play test sound"
                	        	#timeout 15 aplay "${HELLOWORLD}"
					echo "Playing sound now"
	                        	if [ $? != 0 ]
	        	                then
        	        	                echo "[ERROR] aplay failed to complete"
                	        	        exit 4
	                	        else
        	                	        echo "[OK] aplay completed"
	                	        fi
				fi
	                fi
		fi
	fi


	A2DP=$( pactl list sinks short | grep "module-bluez5-device.c" | grep "a2dp_sink" | awk '{print $1}' )
	# check that current inputs have been moved to new sink
	INPUTS=$( pactl list sink-inputs | grep "Sink Input #" | sed "s/Sink Input #//g" )
	if [ "x$INPUTS" != "x" ]
	then
		CURRENT=$( pactl list sink-inputs | grep "Sink:" | awk '{print $2}' )
		if [ "x$CURRENT" != "x$A2DP" ]
		then
			echo "Moving Sink Input #${INPUTS} from $CURRENT to $A2DP"
			pactl move-sink-input ${INPUTS} ${A2DP}
		fi
	fi

	## let other processes do something
	sleep 10

## end infinite while loop
done 

	
