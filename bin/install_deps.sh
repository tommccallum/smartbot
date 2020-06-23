#!/bin/bash

# This will install the different bits to
# cron and logrotate and /opt/smartbot etc
# it is the equivalent of docker

IS_DOCKER=$( cat /proc/1/cgroup | grep docker | wc -l | awk '{print $1}' )
IS_BLUETOOTH=$( ps aux | grep bluetoothd | wc -l )

# get directory that this script is in
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && cd .. && pwd )"
# check for python3
PYTHON=$( which python3 )
LOCAL_CONFIG=$1
DEFAULT_CONF=$2
INSTALL_LOG="${DIR}/log/install.log"
FORCE_INSTALL=0

if [ "x${LOCAL_CONFIG}" == "x" ]
then
  echo "[ERROR] path for configuration not given"
  exit 1
fi

echo "Installing python package 'schedule'"
pip3 install schedule

echo "Installing bluetooth library"
sudo apt-get -y install libbluetooth-dev
echo "Installing python libraries"
pip3 install pybluez
pip3 install evdev
pip3 install numpy
pip3 install psutil
pip3 install python-dateutil
pip3 install pynput

# prepare to copy over a default configuration of some type
if [ "x${DEFAULT_CONF}" == "x" ]
then
  DEFAULT_CONF="$DIR/config/default"
else
  DEFAULT_CONF="$DIR/config/$DEFAULT_CONF"
fi

if [ $IS_DOCKER -gt 0 ]
then
  DEFAULT_CONF="$DIR/config/docker"
fi
echo "[INFO] Installing configuration from '${DEFAULT_CONF}'"

if [ ! -e "$DEFAULT_CONF" ]
then
  echo "[ERROR] Could not find configuration at $DEFAULT_CONF"
  exit 1
fi

echo "[INFO] Installing configuration into ${LOCAL_CONFIG}"
mkdir -p "${LOCAL_CONFIG}"
cp -R "${DEFAULT_CONF}/"* "${LOCAL_CONFIG}/"

echo "[INFO] Creating radio storage directories in '$HOME/media/recent"
mkdir -p $HOME/smartbot/media/recent
mkdir -p $HOME/smartbot/media/podcasts
mkdir -p $HOME/smartbot/media/lets_dance
mkdir -p $HOME/smartbot/media/alarms
mkdir -p $HOME/smartbot/media/radio

echo "[INFO] Creating default alarm directories"
ALARMS=( "all"  "fri"  "mon" "sat" "sun"  "thu"  "tue" "wed"  "weekdays" "weekends" )
for a in "${ALARMS[@]}"
do
  mkdir -p $HOME/smartbot/media/alarms/${a}
done


pushd .
if [ -e "/home/pi/get_iplayer" ]
then
  echo "[INFO] Updating get_iplayer"
  cd /home/pi/get_iplayer
  git pull
else
  echo "[INFO] Installing get_iplayer and its dependencies"
  cd /home/pi
  sudo apt-get -y install ffmpeg perl build-essential curl libhtml-parser-perl \
                            libhttp-cookies-perl libwww-perl libxml-libxml-perl libmojolicious-perl atomicparsley
  git clone https://github.com/get-iplayer/get_iplayer
fi
popd

pushd .
if [ -e "/home/pi/flite" ]
then
  echo "[INFO] Updating flite"
  cd /home/pi/flite
  git pull
else
  echo "[INFO] Installing flite and its dependencies"
  cd /home/pi
  git clone https://github.com/festvox/flite
  cd /home/pi/flite
  ./configure
  make
  make get-voices
fi
popd

echo "[WARNING] This bit requires sudo access"
echo "[INFO] Creating get_iplayer database in /opt/smartbot"
sudo mkdir /opt/smartbot
sudo chown -R pi:www-data /opt/smartbot
sudo chmod g+rw /opt/smartbot
if [ $IS_DOCKER -gt 0 ]
then
  cp ../get_iplayer/programs-docker.txt /opt/smartbot/programs.txt
else
  cp ../get_iplayer/programs-default.txt /opt/smartbot/programs.txt
fi
echo "[INFO] Installing logrotate configuration"
sudo cp $DIR/etc/smartbot.logrotate /etc/logrotate.d/smartbot
echo "[INFO] Installing daily cron task"
crontab -l | grep -v smartbot > existing_crontab~
cat ${DIR}/scheduled_tasks/pi.cron >> existing_crontab~
crontab existing_crontab~
rm existing_crontab~
echo "New crontab file is:"
crontab -l





if [ $IS_DOCKER -gt 0 ]
then
  echo "[WARN] Moving existing radio shows to media/recent"
  if [ -e "./tmp" ]
  then
    mv ./tmp/*.m4a /home/pi/smartbot/media/recent
  fi
else
  pushd .
  echo "[INFO] Downloading initial set of radio podcasts - please wait, this may take some time"
  cd ../get_iplayer/
  python3 get_radio_shows.py
  popd
fi




