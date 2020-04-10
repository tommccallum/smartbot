G# Personal assistant

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
