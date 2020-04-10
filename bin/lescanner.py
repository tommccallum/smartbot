#!/usr/bin/python3

import pwd
import grp
import datetime
import time
import json
import sys
import os
import struct
from ctypes import (CDLL, get_errno)
from ctypes.util import find_library
import signal
import atexit
from socket import (
    socket,
    SOCK_CLOEXEC,
    AF_BLUETOOTH,
    SOCK_RAW,
    BTPROTO_HCI,
    SOL_HCI,
    HCI_FILTER,
)

# global devices variable
g_user=pwd.getpwnam("pi").pw_uid
g_grp=grp.getgrnam("pi").gr_gid
print("{} {}".format(g_user,g_grp))
g_fifo="/home/pi/.config/smartbot/fifos/lescanner.fifo"
g_devices = {}
g_state = {}
g_devices_path = "/home/pi/.config/smartbot/devices.json"
g_device_state = "/home/pi/.config/smartbot/devices.state"
g_sock = None
g_timer = 0
bluez = None

@atexit.register
def clean_exit():
    print("[DEBUG] clean_exit called")
    stop_scan()
    write_state()

def stop_scan():
#    print("Stopping LE scan")
    global g_sock
    global bluez
    global g_timer
    if bluez is not None:
        err = bluez.hci_le_set_scan_enable(
            g_sock.fileno(),
            0,  # 1 - turn on;  0 - turn off
            0, # 0-filtering disabled, 1-filter out duplicates
            1000  # timeout
        )
        if err < 0:
            errnum = get_errno()
            if errnum != 5:
                raise Exception("Error occurred when stopping scan: {} {}".format(
                        errnum,
                        os.strerror(errnum)
                        ))

def exit_request(signal, frame):
    print("[DEBUG] exit_request called")
    stop_scan()
    sys.exit(0)

def reload_request(sig, frame):
    print("[DEBUG] reload_request called")
    print("Received signal: {}".format(sig))
    if sig == signal.SIGUSR1:
        read_devices()

def mean(x):
    sum = 0
    for x1 in x:
      sum += x1
    return sum / len(x)

if not os.geteuid() == 0:
    sys.exit("script only works as root")

btlib = find_library("bluetooth")
if not btlib:
    raise Exception(
        "Can't find required bluetooth libraries"
        " (need to install bluez)"
    )
bluez = CDLL(btlib, use_errno=True)

def start_scan():
    global g_timer
    global g_sock
    global bluez

#    print("Starting LE scan")
    dev_id = bluez.hci_get_route(None)
    if dev_id < 0:
        raise Exception("device not found")

    g_sock = socket(AF_BLUETOOTH, SOCK_RAW | SOCK_CLOEXEC, BTPROTO_HCI)
    g_sock.bind((dev_id,))

    err = bluez.hci_le_set_scan_parameters(g_sock.fileno(), 0, 0x10, 0x10, 0, 0, 1000);
    if err < 0:
        raise Exception("Set scan parameters failed")
        # occurs when scanning is still enabled from previous call


    # allows LE advertising events
    hci_filter = struct.pack(
        "<IQH", 
        0x00000010, 
        0x4000000000000000, 
        0
    )
    g_sock.setsockopt(SOL_HCI, HCI_FILTER, hci_filter)

    err = bluez.hci_le_set_scan_enable(
        g_sock.fileno(),
        1,  # 1 - turn on;  0 - turn off
        0, # 0-filtering disabled, 1-filter out duplicates
        1000  # timeout
    )
    if err < 0:
        errnum = get_errno()
        raise Exception("Error when starting scan: {} {}".format(
            errnum,
            os.strerror(errnum)
        ))
    g_timer = time.time()

def read_devices():
    global g_devices
    if os.path.isfile(g_devices_path):
        file=open(g_devices_path)
        g_devices = json.load(file)
        file.close()

        print("Devices registered")
        print(g_devices)

def write_state():
    with open(g_device_state, "w") as file:
        print("Writing out state to file")
        file.write( json.dumps(g_state, sort_keys=True, indent=4 ) )

def read_state():
    global g_state
    if os.path.isfile(g_device_state):
        with open(g_device_state,"r") as file:
            print("Reading existing state from file")
            g_state = json.load(file)

def write_fifo(event,owner):
    if not os.path.exists(g_fifo):
        with open(g_fifo, "w") as ff:
            ff.write("")
        os.chown(g_fifo, g_user, g_grp )
    with open(g_fifo, "w") as ff:
        print("Writing event to fifo")
        ff.write("{},{},{}".format(time.time(),event,owner))

def start_scan_always():
    while True:
        try:
            start_scan()
            break
        except Exception as err:
            print("Exception caught: {}".format(err))
            stop_scan()
            time.sleep(1)

if __name__ == "__main__":
    # read devices from config file
    read_devices()
    read_state()

    # set handler to detect SIGUSR1 for reload
    signal.signal(signal.SIGINT, exit_request)
    signal.signal(signal.SIGUSR1, reload_request)

    start_scan_always()
    while True:
        if time.time() - g_timer > 5:
            stop_scan()
            time.sleep(1)
            start_scan_always()

        data = g_sock.recv(1024)
        mac = ':'.join("{0:02x}".format(x) for x in data[12:6:-1]).upper()
        raw_rssi = int(data[len(data)-1])
        rssi =  raw_rssi - 255
        #print("[{}] Raw mac {} (RSSI: {})".format(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),mac, rssi))
        if mac not in g_state:
            print("[{}] Found mac {} (RSSI: {})".format(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),mac, rssi))
            g_state[mac] = {"detected":time.time(), "status":0, "data": [rssi]}
        else:
            g_state[mac]["data"] += [rssi]
            g_state[mac]["detected"] = time.time()
            if len(g_state[mac]["data"]) > 3:
                g_state[mac]["data"].pop(0)
        g_state[mac]["avg_rssi"] = mean(g_state[mac]["data"])
        g_state[mac]["last"] = rssi

        if mac in g_devices:
            avg_rssi = g_state[mac]["avg_rssi"]
            status = g_state[mac]["status"]
            print("Found owner of {} rssi={} avg={} status={}".format(mac, rssi, avg_rssi, status))
            ## note we use the actual value for enter, so we respond quickly
            ## and the average for exit so we don't get triggered early
            if rssi > -80 and status == 0:
                write_fifo("enter", mac)
                status = 1
            elif avg_rssi < -80 and status == 1:
                write_fifo("exit", mac)
                status = 0
            if g_state[mac]['status'] != status:
                g_state[mac]['detected'] = time.time()
                g_state[mac]['status'] = status
                print("Found mac {} belonging to {} (RSSI: {}) [{},{:.0f}]".format(mac,g_devices[mac]["owner"],rssi,status,avg_rssi))
                print(g_state)

