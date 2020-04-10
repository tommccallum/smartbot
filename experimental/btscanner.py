#!/usr/bin/python3

import json
import sys

# Note: don't call this file bluetooth.py as it will confuse the name resolution!
import bluetooth
from pybtooth import BluetoothManager

bm = BluetoothManager()
connected = bm.getConnectedDevices()
print(connected)

# if the client device is on scan mode then this will pick it up
nearby_devices = bluetooth.discover_devices(lookup_names=False)

print("found {} devices".format(len(nearby_devices)))

#for name, addr in nearby_devices:
#    print(" %s - %s", (addr, name))
for addr in nearby_devices:
    print( " %s",addr)



exit(1)

file=open("/home/pi/.config/smartbot/devices.json")
j = json.load(file)
file.close()

print(j)


def say(text):
    print(text)
    cmd = "sudo -H -u pi bash -c 'echo \""+text+"\" | sudo -u pi text2wave -eval \"(voice_cmu_us_slt_arctic_clunits)\" > /tmp/say.wav.tmp; cp /tmp/say.wav.tmp /tmp/say.wav'"
    subprocess.run(cmd, shell=True)

status=0

signal.signal(signal.SIGINT, signal_handler)

while True:
    data = sock.recv(1024)
    # print bluetooth address from LE Advert. packet
    mac = ':'.join("{0:02x}".format(x) for x in data[12:6:-1]).upper()
    packet = " ".join("{0:02x}".format(x) for x in data[len(data):0:-1]).upper()
    #print("{} (PACKET) {}".format(mac,packet))
    raw_rssi = int(data[len(data)-1])
    rssi =  raw_rssi - 255
    #print(type(rssi))
    #print("RSSI: {0:02x} {0:d} {0:d}".format(raw_rssi,raw_rssi, rssi))
    #print("{}", rssi)
    if mac in j:
        if j[mac]["owner"] == "Innogen":
            print("Found mac {} belonging to {} (RSSI: {})".format(mac,j[mac]["owner"],rssi))
            if rssi > -70 and status == 0:
                say("Hello Innogen")
                status = 1
            elif rssi < -80 and status == 1:
                say("Goodbye Innogen")
                status = 0
