#!/bin/bash

# Check that Pulseaudio is loaded, if not start it
HOMEDIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"
BLUETOOTH_DEVICE=$(cat "${HOMEDIR}/Bluetooth_Speaker.txt")
EXPECTED_PULSE_APP="pulseaudio"
HELLOWORLD="${HOMEDIR}/../sounds/can_you_hear_me.wav"
TIMEOUT=2       ## expected length of HELLOWORLD sound
SYSTEMCTL=$1
SLEEP_BETWEEN_CHECKS=5

## check if we are already paired with device
## returns 1 if paired, 0 otherwise
function is_paired() {
  local RET=$(bluetoothctl paired-devices | grep "${BLUETOOTH_DEVICE}" | wc -l)
  echo "$RET"
}

function restart_pulseaudio() {
  ## restart pulseaudio for good measure
  local pulse_is_running=$(ps ax | grep pulseaudio | grep -v grep | wc -l)
  if [ ${pulse_is_running} -gt 0 ]
  then
    pulseaudio -k
  fi
  pulseaudio --start
  local pulse_is_running=$(ps ax | grep pulseaudio | grep -v grep | wc -l)
  local pulse_pid=$(ps aux | grep "$EXPECTED_PULSE_APP" | awk '{print $2}')
  if [ "x$pulse_pid" == "x" ]; then
    echo "[ERROR] Pulseaudio is not running after restart, something is really chronic!"
    exit 1
  fi
  echo "${pulse_is_running}"
}

echo "User: ${USER}"

if [ ! -e "${HELLOWORLD}" ]; then
  echo "Could not find ${HELLOWORLD}"
  exit 10
fi

if [ "x${BLUETOOTH_DEVICE}" == "" ]; then
  echo "Could not find bluetooth speaker device address"
  exit 100
fi
echo "[OK] Registered bluetooth device is ${BLUETOOTH_DEVICE}"

# begin an infinite loop where we check if our device has lost
# connection for some reason
FULL_CONNECT_REQUIRED=0
QUICK_CONNECT_COUNT=1
NEW_CONNECTION=0
while true; do

  IS_CONNECTED=$(hcitool con | grep "${BLUETOOTH_DEVICE}" | wc -l)
  if [ ${IS_CONNECTED} -eq 0 ]; then
    echo "No connection found, attempting to reconnect..."

    PULSE_PID=$(ps aux | grep "$EXPECTED_PULSE_APP" | awk '{print $2}')
    if [ "x$PULSE_PID" == "x" ]; then
      echo "Attempting to start Pulseaudio..."
      pulseaudio --start
      PULSE_PID=$(ps aux | grep "$EXPECTED_PULSE_APP" | awk '{print $2}')
      if [ "x$PULSE_PID" == "x" ]; then
        echo "[ERROR] Pulseaudio is not running!"
        exit 1
      else
        echo "Pulseaudio is now running on pid $PULSE_PID"
      fi
    fi

    ## this is the time we want to search our journal from for errors
    WHEN_START=$(date "+%Y-%m-%d %H:%M:%S")
    echo "Journal view from ${WHEN_START}"

    if [ ${FULL_CONNECT_REQUIRED} -eq 0 ]; then
      PAIRED=$(is_paired)
      if [ $PAIRED -eq 0 ]; then
        FULL_CONNECT_REQUIRED=1
      else
        ##
        ## first we want to try a quick connect strategy
        ## where we believe the device is paired already
        ## the user should just need to do a short on cycle for
        ## us to reconnect
        ##
        echo "Attempting a quick connect for bluetooth device"
        sudo bluetoothctl disconnect "${BLUETOOTH_DEVICE}"
        sleep 2
        sudo bluetoothctl connect "${BLUETOOTH_DEVICE}"
        if [ $? -eq 0 ]; then
          echo "Waiting for stuff to happen if it is going to"
          sleep 2 # let stuff happen
          NEW_CONNECTION=1
        else

          HOST_IS_DOWN_MSG="Unable to get Headset Voice gateway SDP record: Host is down"
          IS_HOST_OFF=$(journalctl --since "${WHEN_START}" | grep bluetoothd | grep "$HOST_IS_DOWN_MSG" | wc -l )
          if [ $IS_HOST_OFF -gt 0 ]
          then
            # device is off no point continuing
            echo "Device is most likely turned off, sleep for a bit and then try again"
            sleep 5
            continue
          fi

          ## we get this error if pulseaudio is not running
          NO_A2DP=$(journalctl --since "${WHEN_START}" | grep bluetoothd | grep "a2dp-sink profile connect failed for" | grep "Protocol not available" | wc -l)
          if [ $NO_A2DP -gt 0 ]; then
            echo "error: a2dp-sink profile connect failed"
            restart_pulseaudio
            sleep 1
            continue
          fi

          MSG=$(journalctl --since "${WHEN_START}" | grep bluetoothd | grep "Control: Refusing unexpected connect" | wc -l )
          if [ $MSG -gt 0 ]; then
            echo "error: refusing connection"
            restart_pulseaudio
            sleep 1
            continue
          fi

          MSG=$(journalctl --since "${WHEN_START}" | grep bluetoothd | grep "Unable to get Headset Voice gateway SDP record: Operation already in progress" | wc -l )
          if [ $MSG -gt 0 ]; then
            echo "error: sdp record, retrying"
            restart_pulseaudio
            sleep 1
            continue
          fi


          # if was not successful check why then loop
          DO_QUICK_CONNECT_AGAIN=0
          VALUES=$(journalctl --since "${WHEN_START}" | grep bluetoothd | grep -oP "\(\d+\)$" | sed "s/(//" | sed "s/)//")
          for v in "${VALUES[@]}"; do
            echo "journalctl error code: ${v}"
            if [ "x$v" == "x111" ]; then
              FULL_CONNECT_REQUIRED=0
            fi
            if [ "x$v" == "x107" ]; then
              ### does not need a full reconnect if hits happens
              DO_QUICK_CONNECT_AGAIN=1
              sleep 1
              continue
            fi
          done
          if [ $DO_QUICK_CONNECT_AGAIN -gt 0 ]
          then
            ## most likely scenario is that the user needs to restart
            ## the speaker and is hearing single beeps, we just need
            ## to keep disconnect and connect until we pick it up properly
            QUICK_CONNECT_COUNT=$((QUICK_CONNECT_COUNT+1))
            if [ $QUICK_CONNECT_COUNT -gt 10 ]
            then
              echo "error: quick connect limit reached, full connect required"
              FULL_CONNECT_REQUIRED=1
            else
              sleep 1
              continue
            fi
          fi
          if [ $FULL_CONNECT_REQUIRED -gt 0 ]
          then
            echo "error: full connect required"
            restart_pulseaudio
            sleep 1
            continue
          fi


          # otherwise we just try again
          sleep 1
          continue
        fi
      fi
    fi

    if [ $FULL_CONNECT_REQUIRED -gt 0 ]
    then
      echo "Attempting to do a full reconnect, this may take up to a few minutes on a bad day"
      $HOMEDIR/bluetooth_speaker.expect "${BLUETOOTH_DEVICE}"
      if [ $? != 0 ]; then
        # if was not successful then loop
        echo "full reconnect was unsuccessful"
        sleep 1
        continue
      fi

      ## double check
      PAIRED=$(is_paired)
      if [ ${PAIRED} -eq 0 ]
      then
        echo "Still not paired, lets try again"
        sleep 1
        continue
      fi

      NEW_CONNECTION=1
    fi



    ## -------------------------------------------------------------------------------------------
    ##
    ## if we get here its means we have at least a connection with the speaker ( we hope! )
    ## we should be paired and ready to go so we shouldn't need to do a full reconnect again
    ## even if the device is turned off.
    ##
    ## -------------------------------------------------------------------------------------------
    echo "ok so far, just checking a few more bits, please bare with us"

    # reset our testing variables
    FULL_CONNECT_REQUIRED=0
    QUICK_CONNECT_COUNT=0

    PULSE_SINK=$(pactl list sinks short | grep "module-bluez5-device.c" | awk '{print $1}')
    if [ "x$PULSE_SINK" == "x" ]; then
      echo "[ERROR] pulseaudio '${PULSE_SINK}' has not picked up a bluetooth device, restarting pulseaudio and trying again"
      NEW_CONNECTION=0
      sudo bluetoothctl disconnect "${BLUETOOTH_DEVICE}"
      restart_pulseaudio
      sleep 1
      continue
    else
      echo "[OK] Detected pulseaudio bluetooth device (${PULSE_SINK})"
    fi

    A2DP=$(pactl list | grep -A 18 "bluez" | grep "Active Profile" | awk '{print $3}')
    if [ "x${A2DP}" != "xa2dp_sink" ]; then
      CARD=$(pactl list | grep -B 2 bluez | grep Card | sed "s/Card #//")
      echo "Attempting to set card profile on card #${CARD}"
      pactl set-card-profile ${CARD} a2dp_sink
      A2DP=$(pactl list sinks short | grep "module-bluez5-device.c" | grep "a2dp_sink" | awk '{print $1}')
      if [ "x$A2DP" == "x" ]; then
        echo "[ERROR] Failed to set speaker to a2dp_sink profile, restarting pulseaudio and trying again"
        NEW_CONNECTION=0
        sudo bluetoothctl disconnect "${BLUETOOTH_DEVICE}"
        restart_pulseaudio
        continue
      fi
    fi

    ## check we are the default sink which we should be...
    IS_DEFAULT_SINK=$(pactl info | grep "Default Sink" | grep "bluez_sink" | grep "a2dp_sink" | wc -l)
    if [ $IS_DEFAULT_SINK -eq 0 ]; then
      A2DP=$(pactl list sinks short | grep "module-bluez5-device.c" | grep "a2dp_sink" | awk '{print $1}')
      pactl set-default-sink $A2DP
      if [ $? -gt 0 ]; then
        echo "Failed to set default sink as $A2DP"
        NEW_CONNECTION=0
        sudo bluetoothctl disconnect "${BLUETOOTH_DEVICE}"
        restart_pulseaudio
        continue
      fi
    fi
  fi # end of checking if we are connected

  ## now we are connected, lets do some sanity checks to ensure everthing is as
  ## we expect, cause it quite often is not!!!

  # if a bluetooth device is listed at all
  #	then check its set up properly
  PULSE_SINK=$(pactl list sinks short | grep "module-bluez5-device.c" | grep "a2dp_sink" | awk '{print $1}' | wc -l )
  if [ ${PULSE_SINK} -eq 0 ]; then
    SINK=$(pactl info | grep "Default" | grep -i "sink" | grep "bluez" | wc -l )
    if [ $SINK -gt 0 ]; then
      A2DP=$(pactl list | grep -A 18 "bluez" | grep "Active Profile" | awk '{print $3}' | grep "a2dp_sink" | wc -l )
      if [ ${A2DP} -eq 0 ]; then
        CARD=$(pactl list | grep -B 2 bluez | grep Card | sed "s/Card #//")
        echo "Attempting to select a2dp_sink profile for card ${CARD}"
        pactl set-card-profile ${CARD} a2dp_sink
        if [ $? -gt 0 ]; then
          echo "[ERROR] Failed ot set card ${CARD} profile to a2dp_sink"
          NEW_CONNECTION=0
          sudo bluetoothctl disconnect "${BLUETOOTH_DEVICE}"
          restart_pulseaudio
          continue
        fi
        ## we output this for the reader
        pactl list sinks short | grep "module-bluez5-device.c" | grep "a2dp_sink"

        IS_DEFAULT_SINK_SET=$(pactl list sinks short | grep "module-bluez5-device.c" | grep "a2dp_sink" | awk '{print $1}' | wc -l)
        if [ $IS_DEFAULT_SINK_SET -eq 0 ]; then
          SINK_NAME=$(pactl list sinks short | grep "module-bluez5-device.c" | grep "a2dp_sink" | awk '{print $1}')
          pactl set-default-sink $SINK_NAME
          if [ $? -gt 0 ]; then
            echo "[ERROR] Failed to set default sink, restarting pulseaudio and trying connect."
            NEW_CONNECTION=0
            sudo bluetoothctl disconnect "${BLUETOOTH_DEVICE}"
            restart_pulseaudio
            continue
          fi
        fi
      fi
    fi
  fi


  ## here we test for if the connection was made and pulse was good
  ## but we are stuck on the internal speaker for some reason for some
  ## pulse connections
  ## this is what the module-switch-on-connect is supposed to prevent in /etc/pulse/default.pa
  echo "Checking all applications are using the correct speaker device"
  PULSE_SINK=$(pactl list sinks short | grep "module-bluez5-device.c" | grep "a2dp_sink" | awk '{print $1}')
  INPUTS=$(pactl list sink-inputs | grep "Sink Input #" | sed "s/Sink Input #//g")
  CURRENT_SINKS=$(pactl list sink-inputs | grep "Sink:" | awk '{print $2}')

  for ii in "${!INPUTS[@]}"
  do
    input=${INPUTS[ii]}
    current_sink=${CURRENT_SINKS[ii]}
    if [ "x${input}" != "x" ]; then
      if [ ${current_sink} -ne $PULSE_SINK ]; then
          echo "Moving Sink Input #${input} from ${current_sink} to $PULSE_SINK"
          pactl move-sink-input ${input} ${PULSE_SINK}
          if [ $? -gt 0 ]; then
            echo "Failed to move sink from ${input} to ${PULSE_SINK}"
            NEW_CONNECTION=0
            sudo bluetoothctl disconnect "${BLUETOOTH_DEVICE}"
            restart_pulseaudio
            continue
          fi
      fi
    fi
  done

  ## a sign of success for a2dp is this: Watching system buttons on /dev/input/event3 (mac_address) under systemd-logind
  ## kernel: input: D0:8A:55:00:9C:27 as /devices/virtual/input/input8
  ## this seems to take a bit of time to do so lets sleep for 2
  sleep 2
  A2DP_INPUT=$(journalctl --since "${WHEN_START}" | grep kernel | grep "${BLUETOOTH_DEVICE}" | grep "input:" | grep "as /devices/virtual/input" | wc -l)
  if [ ${A2DP_INPUT} -eq 0 ]; then
    ## hmmm.. something not quite right, lets try again as we do not have proper control
    echo "Failed to find virtual input for bluetooth device, reconnecting"
    NEW_CONNECTION=0
    sudo bluetoothctl disconnect "${BLUETOOTH_DEVICE}"
    echo $(restart_pulseaudio) > /dev/null
    sleep 1
    continue
  fi



  if [ $NEW_CONNECTION -gt 0 ]
  then
    NEW_CONNECTION=0
    echo "[OK] New connection found, attempting to speak"
    timeout $TIMEOUT aplay "${HELLOWORLD}"
    if [ $? != 0 ]; then
      echo "[ERROR] helloworld sound failed to play, restarting pulseaudio and reconnecting"
      NEW_CONNECTION=0
      sudo bluetoothctl disconnect "${BLUETOOTH_DEVICE}"
      restart_pulseaudio
      continue
    else
      echo "[OK] we are connected successfully"
    fi
  fi

  ## by this point we should have what we want for a little while
  ## let other processes do something
  echo "All good, sleeping for $SLEEP_BETWEEN_CHECKS seconds"
  sleep $SLEEP_BETWEEN_CHECKS

  ## end infinite while loop
done
