#!/bin/bash

# Check that Pulseaudio is loaded, if not start it
HOMEDIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"
USERHOME=$( echo "$HOMEDIR" | awk -F '/' '{print "/" $2 "/" $3}' )
CONFIGDIR="$USERHOME/.config/smartbot"
VERBOSE=0
EXPECTED_PULSE_APP="pulseaudio"


##
## The following variables can be overridden by devices.json
##

# start sound to play on successful connection
HELLOWORLD="${HOMEDIR}/../sounds/can_you_hear_me.wav"
# lockfile to use
LOCKFILE="/tmp/smartbot_connected.lock"
# expected length of HELLOWORLD sound
TIMEOUT=2
# how long to sleep between checks of the device in seconds
SLEEP_BETWEEN_CHECKS=5




if [ "$1" == "-v" ]; then
  VERBOSE=1
fi

if [ ! -e "$CONFIGDIR" ]
then
  echo "configuration directory does not exist"
  exit 1
fi
if [ ! -e "${CONFIGDIR}/bluetooth_devices.conf" ]
then
  echo "bluetooth_devices.conf is missing from ${CONFIGDIR}"
  exit 1
fi

source "${CONFIGDIR}/bluetooth_devices.conf"

if [ "x$DEVICES" == "" ]
then
  echo "No devices specified."
  exit 1
fi

BLUETOOTH_DEVICE="${DEVICES[0]}"
if [ "x${BLUETOOTH_DEVICE}" == "" ]; then
  echo "No device specified in array."
  exit 1
fi




function msg() {
  echo "[$(date "+%Y-%m-%d %H:%M:%S")] [INFO ] $1"
}

function debug() {
  if [ $VERBOSE -gt 0 ]; then
    echo "[$(date "+%Y-%m-%d %H:%M:%S")] [DEBUG] $1"
  fi
}

function error() {
  echo "[$(date "+%Y-%m-%d %H:%M:%S")] [ERROR] $1"
}

function warn() {
  echo "[$(date "+%Y-%m-%d %H:%M:%S")] [WARN ] $1"
}

## check if we are already paired with device
## returns 1 if paired, 0 otherwise
function is_paired() {
  local RET=$(bluetoothctl paired-devices | grep "${BLUETOOTH_DEVICE}" | wc -l)
  echo "$RET"
}

function restart_pulseaudio() {
  ## restart pulseaudio for good measure
  local pulse_is_running=$(ps ax | grep pulseaudio | grep -v grep | wc -l)
  if [ ${pulse_is_running} -gt 0 ]; then
    pulseaudio -k
  fi
  pulseaudio --start
  local pulse_is_running=$(ps ax | grep pulseaudio | grep -v grep | wc -l)
  local pulse_pid=$(ps aux | grep "$EXPECTED_PULSE_APP" | awk '{print $2}')
  if [ "x$pulse_pid" == "x" ]; then
    error "Pulseaudio is not running after restart, something is really chronic!"
    exit 1
  fi
  echo "${pulse_is_running}"
}

function remove_lockfile() {
  if [ -e "${LOCKFILE}" ]; then
    msg "Clearing old lock file to show that we are not connected"
    rm -f "${LOCKFILE}"
  fi
}

function evtest_and_exit() {
    local evtest_pid
    evtest /dev/input/event$i &
    evtest_pid=$!
    sleep 1  # give evtest time to produce output
    kill $evtest_pid
}


if [ ! -e "${HELLOWORLD}" ]; then
  error "Could not find ${HELLOWORLD}"
  exit 1
fi

if [ "x${USER}" == "xroot" ]
then
  error "This script needs to run as a user not 'root'. User needs to be in sudo group."
  exit 1
fi

#
# =======================================================
#  Main script starts here
# =======================================================
#

remove_lockfile

FIRST_START=1
while true; do

  debug "Checking bluetooth device '${BLUETOOTH_DEVICE}'"

  # begin an infinite loop where we check if our device has lost
  # connection for some reason
  FULL_CONNECT_REQUIRED=0
  QUICK_CONNECT_COUNT=1
  NEW_CONNECTION=0
  IS_CONNECTED=$(hcitool con | grep "${BLUETOOTH_DEVICE}" | wc -l)

  if [ ${IS_CONNECTED} -eq 0 ]; then
    #
    #   FULL_CONNECT_REQUIRED if device is not paired OR error 107 OR see 10 errors that are not resolved
    #
    #   otherwise QUICK_CONNECT
    #
    remove_lockfile

    info "No connection found, attempting to reconnect..."
    CONNECTION_DURATION_START=$(date "+%s")

    PULSE_PID=$(ps aux | grep "$EXPECTED_PULSE_APP" | awk '{print $2}')
    if [ "x$PULSE_PID" == "x" ]; then
      info "Attempting to start Pulseaudio..."
      pulseaudio --start
      PULSE_PID=$(ps aux | grep "$EXPECTED_PULSE_APP" | awk '{print $2}')
      if [ "x$PULSE_PID" == "x" ]; then
        error "Pulseaudio is not running!"
        exit 1
      else
        msg "Pulseaudio is now running on pid $PULSE_PID"
      fi
    fi

    ## this is the time we want to search our journal from for errors
    WHEN_START=$(date "+%Y-%m-%d %H:%M:%S")
    msg "Journal view from ${WHEN_START}"

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
        msg "Attempting a quick connect for bluetooth device"
        sudo bluetoothctl disconnect "${BLUETOOTH_DEVICE}"
        sleep 2
        sudo bluetoothctl connect "${BLUETOOTH_DEVICE}"
        if [ $? -eq 0 ]; then
          msg "Waiting for stuff to happen if it is going to"
          sleep 5 # let stuff happen
          NEW_CONNECTION=1
        else

          HOST_IS_DOWN_MSG="Unable to get Headset Voice gateway SDP record: Host is down"
          IS_HOST_OFF=$(journalctl --since "${WHEN_START}" | grep bluetoothd | grep "$HOST_IS_DOWN_MSG" | wc -l)
          if [ $IS_HOST_OFF -gt 0 ]; then
            # device is off no point continuing
            msg "Device is most likely turned off, sleep for a bit and then try again"
            sleep 1
            continue
          fi

          ## we get this error if pulseaudio is not running
          NO_A2DP=$(journalctl --since "${WHEN_START}" | grep bluetoothd | grep "a2dp-sink profile connect failed for" | grep "Protocol not available" | wc -l)
          if [ $NO_A2DP -gt 0 ]; then
            error "a2dp-sink profile connect failed"
            echo $(restart_pulseaudio) >/dev/null
            sleep 1
            continue
          fi

          MSG=$(journalctl --since "${WHEN_START}" | grep bluetoothd | grep "Control: Refusing unexpected connect" | wc -l)
          if [ $MSG -gt 0 ]; then
            error "puleaudio is refusing connection"
            echo $(restart_pulseaudio) >/dev/null
            sleep 1
            continue
          fi

          MSG=$(journalctl --since "${WHEN_START}" | grep bluetoothd | grep "Unable to get Headset Voice gateway SDP record: Operation already in progress" | wc -l)
          if [ $MSG -gt 0 ]; then
            error "sdp record, retrying"
            echo $(restart_pulseaudio) >/dev/null
            sleep 1
            continue
          fi

          # if was not successful check why then loop
          DO_QUICK_CONNECT_AGAIN=0
          VALUES=( $(journalctl --since "${WHEN_START}" | grep bluetoothd | grep -oP "\(\d+\)$" | sed "s/(//" | sed "s/)//") )
          for v in "${VALUES[@]}"; do
            error "journalctl error code found: ${v}"
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
          if [ $DO_QUICK_CONNECT_AGAIN -gt 0 ]; then
            ## most likely scenario is that the user needs to restart
            ## the speaker and is hearing single beeps, we just need
            ## to keep disconnect and connect until we pick it up properly
            QUICK_CONNECT_COUNT=$((QUICK_CONNECT_COUNT + 1))
            if [ $QUICK_CONNECT_COUNT -gt 10 ]; then
              error "quick connect limit reached, full connect required"
              FULL_CONNECT_REQUIRED=1
            else
              sleep 1
              continue
            fi
          fi
          if [ $FULL_CONNECT_REQUIRED -gt 0 ]; then
            error "full connect required"
            echo $(restart_pulseaudio) >/dev/null
            sleep 1
            continue
          fi

          # otherwise we just try again
          sleep 1
          continue
        fi
      fi
    fi # end of quick connect attempt

    if [ $FULL_CONNECT_REQUIRED -gt 0 ]; then
      msg "Attempting to do a full reconnect, this may take up to a few minutes on a bad day"
      $HOMEDIR/bluetooth_speaker.expect "${BLUETOOTH_DEVICE}"
      if [ $? != 0 ]; then
        # if was not successful then loop
        msg "full reconnect was unsuccessful"
        echo $(restart_pulseaudio) >/dev/null
        sleep 1
        continue
      fi

      ## double check
      PAIRED=$(is_paired)
      if [ ${PAIRED} -eq 0 ]; then
        msg "Still not paired, lets try again"
        echo $(restart_pulseaudio) >/dev/null
        sleep 1
        continue
      fi

      FULL_CONNECT_REQUIRED=0
      NEW_CONNECTION=1
    fi # end of full connect attempt
  fi # end of no connection condition

  ## -------------------------------------------------------------------------------------------
  ##
  ## if we get here its means we have at least a connection with the speaker ( we hope! )
  ## we should be paired and ready to go so we shouldn't need to do a full reconnect again
  ## even if the device is turned off.
  ##
  ## -------------------------------------------------------------------------------------------
  msg "ok so far, just checking a few more bits, please bare with us"

  # reset our testing variables
  FULL_CONNECT_REQUIRED=0
  QUICK_CONNECT_COUNT=0

  pactl list sinks short
  PULSE_SINK=$(pactl list sinks short | grep "module-bluez5-device.c" | awk '{print $1}')
  if [ "x$PULSE_SINK" == "x" ]; then
    error "pulseaudio '${PULSE_SINK}' has not picked up a bluetooth device, restarting pulseaudio and trying again"
    NEW_CONNECTION=0
    sudo bluetoothctl disconnect "${BLUETOOTH_DEVICE}"
    echo $(restart_pulseaudio) >/dev/null
    sleep 1
    continue
  else
    info "detected pulseaudio bluetooth device (${PULSE_SINK})"
  fi

  #    A2DP=$(pactl list | grep -A 18 "bluez" | grep "Active Profile" | awk '{print $3}')
  #    if [ "x${A2DP}" != "xa2dp_sink" ]; then
  #      CARD=$(pactl list | grep -B 2 bluez | grep Card | sed "s/Card #//")
  #      echo "Attempting to set card profile on card #${CARD}"
  #      pactl set-card-profile ${CARD} a2dp_sink
  #      A2DP=$(pactl list sinks short | grep "module-bluez5-device.c" | grep "a2dp_sink" | awk '{print $1}')
  #      if [ "x$A2DP" == "x" ]; then
  #        echo "[ERROR] Failed to set speaker to a2dp_sink profile, restarting pulseaudio and trying again"
  #        NEW_CONNECTION=0
  #        sudo bluetoothctl disconnect "${BLUETOOTH_DEVICE}"
  #        restart_pulseaudio
  #        continue
  #      fi
  #    fi

  #    ## check we are the default sink which we should be...
  #    IS_DEFAULT_SINK=$(pactl info | grep "Default Sink" | grep "bluez_sink" | grep "a2dp_sink" | wc -l)
  #    if [ $IS_DEFAULT_SINK -eq 0 ]; then
  #      A2DP=$(pactl list sinks short | grep "module-bluez5-device.c" | grep "a2dp_sink" | awk '{print $1}')
  #      pactl set-default-sink $A2DP
  #      if [ $? -gt 0 ]; then
  #        echo "Failed to set default sink as $A2DP"
  #        NEW_CONNECTION=0
  #        sudo bluetoothctl disconnect "${BLUETOOTH_DEVICE}"
  #        restart_pulseaudio
  #        continue
  #      fi
  #    fi
  #  fi # end of checking if we are connected

  ## now we are connected, lets do some sanity checks to ensure everthing is as
  ## we expect, cause it quite often is not!!!

  # if a bluetooth device is listed at all
  #	then check its set up properly
  msg "Check pulseaudio has set up the a2dp sink properly"
  PULSE_SINK=$(pactl list sinks short | grep "module-bluez5-device.c" | grep "a2dp_sink" | awk '{print $1}' | wc -l)
  if [ ${PULSE_SINK} -eq 0 ]; then
    msg "Bluez device not set as sink, checking to see if its the default sink"
    SINK=$(pactl info | grep "Default" | grep -i "sink" | grep "bluez" | wc -l)
    if [ $SINK -gt 0 ]; then
      msg "Its not, so lets check the active profile"
      A2DP=$(pactl list | grep -A 18 "bluez" | grep "Active Profile" | awk '{print $3}' | grep "a2dp_sink" | wc -l)
      if [ ${A2DP} -eq 0 ]; then
        msg "Its not the active profile, so lets check the card"
        CARD=$(pactl list | grep -B 2 bluez | grep Card | sed "s/Card #//")
        msg "Attempting to select a2dp_sink profile for card ${CARD}"
        pactl set-card-profile ${CARD} a2dp_sink
        if [ $? -gt 0 ]; then
          error "Failed to set card ${CARD} profile to a2dp_sink"
          NEW_CONNECTION=0
          sudo bluetoothctl disconnect "${BLUETOOTH_DEVICE}"
          echo $(restart_pulseaudio) >/dev/null
          continue
        fi
      fi

      msg "So now lets check to see if its a listed sink"
      ## we output this for the reader
      pactl list sinks short | grep "module-bluez5-device.c" | grep "a2dp_sink"
      IS_DEFAULT_SINK_SET=$(pactl list sinks short | grep "module-bluez5-device.c" | grep "a2dp_sink" | awk '{print $1}' | wc -l)
      if [ $IS_DEFAULT_SINK_SET -eq 0 ]; then
        msg "No, lets try setting the default sink"
        SINK_NAME=$(pactl list sinks short | grep "module-bluez5-device.c" | grep "a2dp_sink" | awk '{print $1}')
        pactl set-default-sink $SINK_NAME
        if [ $? -gt 0 ]; then
          error "Failed to set default sink, restarting pulseaudio and trying connect."
          NEW_CONNECTION=0
          sudo bluetoothctl disconnect "${BLUETOOTH_DEVICE}"
          echo $(restart_pulseaudio) >/dev/null
          continue
        fi
      fi
    fi
  fi

  ## here we test for if the connection was made and pulse was good
  ## but we are stuck on the internal speaker for some reason for some
  ## pulse connections
  ## this is what the module-switch-on-connect is supposed to prevent in /etc/pulse/default.pa
  msg "Checking all applications are using the correct speaker device"
  PULSE_SINK=$(pactl list sinks short | grep "module-bluez5-device.c" | grep "a2dp_sink" | awk '{print $1}')
  INPUTS=( $(pactl list sink-inputs | grep "Sink Input #" | sed "s/Sink Input #//g") )
  CURRENT_SINKS=( $(pactl list sink-inputs | grep "Sink:" | awk '{print $2}') )

  for ii in "${!INPUTS[@]}"; do
    input=${INPUTS[$ii]}
    current_sink=${CURRENT_SINKS[$ii]}
    if [ "x${input}" != "x" ]; then
      if [ ${current_sink} -ne $PULSE_SINK ]; then ## @todo this is still causing "too many argument errors"
        msg "Moving Sink Input #${input} from ${current_sink} to $PULSE_SINK"
        pactl move-sink-input ${input} ${PULSE_SINK}
        if [ $? -gt 0 ]; then
          error "Failed to move sink from ${input} to ${PULSE_SINK}"
          NEW_CONNECTION=0
          sudo bluetoothctl disconnect "${BLUETOOTH_DEVICE}"
          echo $(restart_pulseaudio) >/dev/null
          continue
        fi
      fi
    fi
  done

  ## a sign of success for a2dp is this: Watching system buttons on /dev/input/event3 (mac_address) under systemd-logind
  ## kernel: input: D0:8A:55:00:9C:27 as /devices/virtual/input/input8
  ## this seems to take a bit of time to do so lets sleep for another 2
  msg "Checking virtual device has been setup properly"
  VIRTUAL_INPUT=""
  VIRTUAL_INPUT_PATHS=$( find /dev/input -iname "event*" )
  for v in "${VIRTUAL_INPUT_PATHS[@]}":
  do
    CHECK_INPUT=$( timeout 1 evtest $v | head -n 3 | grep "${BLUETOOTH_DEVICE}" | wc -l )
    if [ $CHECK_INPUT -gt 0 ]
    then
      VIRTUAL_INPUT=$v
      break
    fi
  done
  if [ "x$VIRTUAL_INPUT" == "x" ]
  then
    sleep 2
    A2DP_INPUT=$(journalctl --since "${WHEN_START}" | grep kernel | grep "${BLUETOOTH_DEVICE}" | grep "input:" | grep "as /devices/virtual/input" | wc -l)
    if [ ${A2DP_INPUT} -eq 0 ]; then
      ## hmmm.. something not quite right, lets try again as we do not have proper control
      error "Failed to find virtual input for bluetooth device, reconnecting"
      NEW_CONNECTION=0
      sudo bluetoothctl disconnect "${BLUETOOTH_DEVICE}"
      echo $(restart_pulseaudio) >/dev/null
      sleep 1
      continue
    fi
  fi

  if [ $NEW_CONNECTION -gt 0 ]; then
    NEW_CONNECTION=0

    CONNECTION_DURATION_END=$(date "+%s")
    DURATION=$((CONNECTION_DURATION_END - CONNECTION_DURATION_START))
    msg "Connection time was ${DURATION} seconds"

    msg "New connection found, attempting to speak"
    timeout $TIMEOUT aplay "${HELLOWORLD}"
    if [ $? != 0 ]; then
      error "helloworld sound failed to play, restarting pulseaudio and reconnecting"
      NEW_CONNECTION=0
      sudo bluetoothctl disconnect "${BLUETOOTH_DEVICE}"
      echo $(restart_pulseaudio) >/dev/null
      continue
    else
      msg "we are connected successfully"
      echo "$(date "+%s"),CONNECTED" > $LOCKFILE
    fi
  else
    if [ $FIRST_START -gt 0 ]
    then
      msg "we are connected successfully"
      echo "$(date "+%s"),CONNECTED" > $LOCKFILE
      FIRST_START=0
    fi
  fi

  ## by this point we should have what we want for a little while
  ## let other processes do something
  debug "All good, sleeping for $SLEEP_BETWEEN_CHECKS seconds"
  sleep $SLEEP_BETWEEN_CHECKS
done # end while loop
