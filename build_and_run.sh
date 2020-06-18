#!/bin/bash

USER_ID=$(id -u)

# check and kill any running docker container called april
APRIL_EXISTS=$( docker ps -a | grep "april$" | wc -l )
if [ $APRIL_EXISTS -gt 0 ]
then
  echo "Stopping existing docker container called 'april'"
  docker stop april
  APRIL_EXISTS=$( docker ps -a | grep "april$" | wc -l )
  if [ $APRIL_EXISTS -gt 0 ]
  then
    echo "Failed to stop docker instance called 'april', please fix and then re-run"
    exit 1
  fi
fi


echo "Building docker container, please wait..."
docker build . > docker-build.log
CONTAINER_ID=$( tail -n 1 docker-build.log | awk '{print $3}' )
echo "Built container ${CONTAINER_ID}"
#-v /tmp/.X11-unix:/tmp/.X11-unix --device /dev/snd
echo "Running container named 'april'"
docker run --name april --volume=/run/user/${USER_ID}/pulse:/run/user/1000/pulse --rm --privileged --net=host -dit ${CONTAINER_ID} bash
docker ps -a | grep april
echo "Running smartbot for first time to install"
docker exec --user pi -i -t april bash -c "cd /home/pi/smartbot/bin && ./smartbot"
echo
echo "*** Use 'docker attach april' to get to command prompt for container ***"
echo "*** Use CTRL-P CTRL-Q to quit docker instance without removing container ***"
echo
