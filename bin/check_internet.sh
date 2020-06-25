#!/bin/bash

# google DNS servers
CHECK_IP="8.8.8.8"
NETWORK_LOCKFILE="/tmp/smartbot_network.lock"
INTERNET_LOCKFILE="/tmp/smartbot_internet.lock"
INTERNET_CONNECTED=0
LOCAL_NETWORK_CONNECTED=0

if [ -e "$NETWORK_LOCKFILE" ]
then
  LOCAL_NETWORK_CONNECTED=1
  echo "[${NOW}] network state detected as present"
fi
if [ -e "$INTERNET_LOCKFILE" ]
then
  INTERNET_CONNECTED=1
  echo "[${NOW}] internet state detected as present"
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

  if [ $CHECK_LOCAL_NETWORK -gt 1 ]
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
    PING=$( ping -c $CHECK_IP | grep "1 received" | wc -l )

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

  fi

done