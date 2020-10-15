#!/bin/bash

# Check if network and internet is down
# It uses the existence of a file to indicate the status to any interested
# process.


CHECK_IP="8.8.8.8"                                # Google DNS servers are used to test internet connectivity
NETWORK_LOCKFILE="/tmp/smartbot_network.lock"
INTERNET_LOCKFILE="/tmp/smartbot_internet.lock"
INTERNET_CONNECTED=0                              # status flag for tracking internet connectivity
LOCAL_NETWORK_CONNECTED=0                         # status flag for tracking local network connectivity


#
# On startup we get the current state of the network.
#
NOW=$(date "+%Y-%m-%d %H:%M:%S")
if [ -e "$NETWORK_LOCKFILE" ]
then
  LOCAL_NETWORK_CONNECTED=1
  echo "[${NOW}] startup, network state detected as present"
else
  echo "[${NOW}] startup, network state not detected"
fi
if [ -e "$INTERNET_LOCKFILE" ]
then
  INTERNET_CONNECTED=1
  echo "[${NOW}] startup, internet state detected as present"
else
  echo "[${NOW}] startup, internet state not detected"
fi


while true
do
  IPV4=( $( ifconfig | grep "inet " | grep -v "127.0.0.1" | awk '{print $2}' ) )
  NOW=$(date "+%Y-%m-%d %H:%M:%S")

  #
  #  Local network check
  #  to test remove the cable :)
  #

  CHECK_LOCAL_NETWORK=0
  for addr in "${IPV4[@]}"
  do
    if [ "x$addr" != "x" ]
    then
      CHECK_LOCAL_NETWORK=1
      break
    fi
  done

  if [ $CHECK_LOCAL_NETWORK -gt 0 ]
  then
    if [ $LOCAL_NETWORK_CONNECTED -eq 0 ]
    then
      echo "$NOW" > $NETWORK_LOCKFILE
      LOCAL_NETWORK_CONNECTED=1
      echo "[${NOW}] local network restored with IP ${addr}"
    fi
  else
    if [ $LOCAL_NETWORK_CONNECTED -gt 0 ]
    then
      echo "[${NOW}] local network lost"
      LOCAL_NETWORK_CONNECTED=0
      rm -f $NETWORK_LOCKFILE
    fi
  fi

  if [ $LOCAL_NETWORK_CONNECTED -gt 0 ]
  then
    #
    # Check internet connection by pinging the CHECK_IP
    #
    PING=$( ping -c 1 $CHECK_IP | grep "1 received" | wc -l )

    if [ $PING -eq 0 ]
    then
      if [ $INTERNET_CONNECTED -gt 0 ]
      then
        echo "[${NOW}] internet lost"
        INTERNET_CONNECTED=0
        rm -f $INTERNET_LOCKFILE
      fi
    else
      if [ $INTERNET_CONNECTED -eq 0 ]
      then
        echo "[${NOW}] internet restored"
        INTERNET_CONNECTED=1
        echo "$NOW" > $INTERNET_LOCKFILE
      fi
    fi
  else
    if [ -e "$INTERNET_LOCKFILE" ]
    then
      echo "[${NOW}] internet lost"
      INTERNET_CONNECTED=0
      rm -f $INTERNET_LOCKFILE
    fi
  fi

  sleep 1
done