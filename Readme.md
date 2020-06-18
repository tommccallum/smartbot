# Personal assistant

## Technologies

- Raspberry Pi
- Bluetooth Speaker

## Software

- Python 3
```
sudo apt install libbluetooth-dev
pip install pybluez
```
- get_iplayer
-- https://github.com/get-iplayer/get_iplayer
- festvox
-- http://festvox.org/festival/index.html
-- https://wiki.archlinux.org/index.php/Festival#Manually
- mplayer
-- http://www.mplayerhq.hu/DOCS/tech/slave.txt
- m3u for playlists
-- https://en.wikipedia.org/wiki/M3U
- schedule for python
-- https://github.com/dbader/schedule
- Apache2
- PHP 7 (libapache2-mod-php)

## Techniques

- Uses a FIFO file to communicate with mplayer instance to allow pause and plan

# Similar projects

# Text to Speech

- http://festvox.org/festival/index.html
- https://github.com/mozilla/TTS/tree/dev


# Architecture

- User Context manages the current operation of the bluetooth speaker
- Each state adds sets of abilities to the User Context Queue
- When each state has been loaded, it then calls UserContext.execute, which will then run each ability in turn


# Permissions

- Add user to the following:
-- lp
-- bluetooth
-- www-data

# PulseAudio

- add the following to /etc/pulse/default.pa
```
load-module module-switch-on-connect
```
- install bluez for bluetooth
- install python-gobject
- pactl load-module module-bluetooth-discover
- check /var/log/syslog if you get errors when trying to connect to bluetooth

# Bluetooth

- use bluetoothctl manually first to check connectivity
```
$ sudo bluetoothctl
> scan on
# wait for device to be detected
> trust XXX
> pair XXX
> connect XXX
```

# Updatable programs.txt

```
sudo mkdir /opt/smartbot
sudo chown pi:www-data /opt/smartbot
sudo chmod g+ws /opt/smartbot
cp get_iplayer/programs.txt /opt/smartbot
```

# Sensing distance

- https://www.raspberrypi.org/forums/viewtopic.php?t=47466
- can see bluetooth le devices with this, but cannot get rssi
```
sudo hcitool lescan --passive
``
- this works once connected
```
sudo hcitool rssi <device>
```
- https://www.quora.com/How-do-I-calculate-distance-in-meters-km-yards-from-rssi-values-in-dBm-of-BLE-in-android
Installation instructions for R-Pi from clean Raspbian lite image

* assumes connected to internet

- Dependencies
$ sudo apt update
$ sudo apt upgrade
$ sudo apt install python-pip3 pulseaudio git mplayer apache2 php
$ pip3 install schedule evdev

- Download
$ git clone https://github.com/tommccallum/BluetoothMusicPlayer

- Install get_iplayer
$ git clone https://github.com/get-iplayer/get_iplayer
$ sudo perl -MCPAN -e shell
> install HTML::Entities
> install HTTP::Cookies
> install LWP::ConnCache


- Setup
$ mkdir -p $HOME/Radio/tmp
$ mkdir -p $HOME/Radio/keep

- Installation
$ cd BluetoothMusicPlayer
$ check_dependencies.sh
$ ./install_festival_voices.sh
$ cp scheduled/* /etc/cron.daily
$ ./retrieveChildrensProgrammes.sh

- Install Web Interface
$ sudo a2enmod cgi
$ ./install_web_interface.sh
