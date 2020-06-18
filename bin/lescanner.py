#!/usr/bin/python3 -u

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
import logging

TIME_AWAY_IS_EXIT_IN_SECS=10
SOCKET_TIMEOUT_IN_SECS=1
SCAN_TIMEOUT_IN_MS=200

# global devices variable
g_user=pwd.getpwnam("pi").pw_uid
g_grp=grp.getgrnam("pi").gr_gid
print("Running as user '{}' in group '{}'".format(g_user,g_grp))
g_fifo="/home/pi/.config/smartbot/fifos/lescanner.fifo"
g_devices = {}
g_state = {}
g_devices_path = "/home/pi/.config/smartbot/devices.json"
g_device_state = "/home/pi/.config/smartbot/devices.state"
g_sock = None
g_timer = 0
bluez = None
g_ready = False
g_stop = False

@atexit.register
def clean_exit():
    logging.debug("clean_exit called")
    stop_scan()
    write_state()

def stop_scan():
    logging.debug("function enter")
#    print("Stopping LE scan")
    global g_sock
    global bluez
    global g_timer
    if g_sock is None:
        return
    if bluez is None:
        return
    logging.debug("setting scan off")
    err = bluez.hci_le_set_scan_enable(
        g_sock.fileno(),
        0,  # 1 - turn on;  0 - turn off
        0, # 0-filtering disabled, 1-filter out duplicates
        SCAN_TIMEOUT_IN_MS  # timeout
    )
    logging.debug("setting scan off - completed")
    if err < 0:
        errnum = get_errno()
        if errnum != 5:
            raise Exception("Error occurred when stopping scan: {} {}".format(
                    errnum,
                    os.strerror(errnum)
                    ))

def exit_request(signal, frame):
    global g_stop
    logging.debug("*** exit_request called ***")
    g_stop = True
    stop_scan()
    logging.debug("exiting application")
    sys.exit(0)

def reload_request(sig, frame):
    logging.debug(" reload_request called")
    logging.debug("Received signal: {}".format(sig))
    if sig == signal.SIGUSR1:
        read_devices()

def mean(x):
    sum = 0
    for x1 in x:
      sum += x1
    return sum / len(x)


def start_scan():
    logging.debug("function enter")
    global g_timer
    global g_sock
    global bluez

#    print("Starting LE scan")
    dev_id = bluez.hci_get_route(None)
    if dev_id < 0:
        return False

    g_sock = socket(AF_BLUETOOTH, SOCK_RAW | SOCK_CLOEXEC, BTPROTO_HCI)
    g_sock.bind((dev_id,))

    err = bluez.hci_le_set_scan_parameters(g_sock.fileno(), 0, 0x10, 0x10, 0, 0, SCAN_TIMEOUT_IN_MS);
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
    g_sock.settimeout(SOCKET_TIMEOUT_IN_SECS)
    err = bluez.hci_le_set_scan_enable(
        g_sock.fileno(),
        1,  # 1 - turn on;  0 - turn off
        0, # 0-filtering disabled, 1-filter out duplicates
        SCAN_TIMEOUT_IN_MS  # timeout
    )
    if err < 0:
        errnum = get_errno()
        raise Exception("Error when starting scan: {} {}".format(
            errnum,
            os.strerror(errnum)
        ))
    g_timer = time.time()
    return True

def read_devices():
    global g_devices
    if os.path.isfile(g_devices_path):
        file=open(g_devices_path)
        g_devices = json.load(file)
        file.close()

        logging.debug("Devices registered")
        logging.debug(g_devices)

def write_state():
    """Write out state, IF we have got as far as reading it in!"""
    global g_ready
    if g_ready:
        with open(g_device_state, "w") as file:
            logging.debug("Writing out state to file")
            file.write( json.dumps(g_state, sort_keys=True, indent=4 ) )

def read_state():
    global g_state
    if os.path.isfile(g_device_state):
        with open(g_device_state,"r") as file:
            logging.debug("Reading existing state from file")
            g_state = json.load(file)
            logging.debug(g_state)

    for mac in g_state:
        g_state[mac]["detected"] = time.time()

def write_fifo(event,owner):
    logging.debug("function enter")
    d = os.path.dirname(g_fifo)
    if not os.path.isdir(d):
        logging.debug("creating directory {}".format(d))
        os.mkdirs(d)
    if not os.path.exists(g_fifo):
        with open(g_fifo, "w") as ff:
            ff.write("")
        os.chown(g_fifo, g_user, g_grp )
    with open(g_fifo, "w") as ff:
        logging.debug("Writing event to fifo")
        ff.write("{},{},{}\n".format(time.time(),event,owner))
    logging.debug("function exit")

def start_scan_always():
    logging.debug("function enter")
    while True:
        try:
            if not start_scan():
                return False
            break
        except Exception as err:
            logging.debug("Exception caught: {}".format(err))
            stop_scan()
            time.sleep(1)
    return True

def search_for_event():
    logging.debug("function enter {}".format(g_sock.getblocking()))
    try:
        data = g_sock.recv(1024)
    except:
        return
    mac = ':'.join("{0:02x}".format(x) for x in data[12:6:-1]).upper()
    raw_rssi = int(data[len(data) - 1])
    rssi = raw_rssi - 255
    # print("[{}] Raw mac {} (RSSI: {})".format(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),mac, rssi))
    if mac not in g_state:
        logging.debug("[{}] Found unknown mac {} (RSSI: {})".format(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), mac, rssi))
        g_state[mac] = {"detected": time.time(), "status": 0, "data": [rssi]}
    else:
        logging.debug("[{}] Found known mac {} (RSSI: {})".format(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), mac, rssi))
        g_state[mac]["data"] += [rssi]
        g_state[mac]["detected"] = time.time()
        if len(g_state[mac]["data"]) > 3:
            g_state[mac]["data"].pop(0)
    g_state[mac]["avg_rssi"] = mean(g_state[mac]["data"])
    g_state[mac]["last"] = rssi

    if mac in g_devices:
        avg_rssi = g_state[mac]["avg_rssi"]
        status = g_state[mac]["status"]
        logging.debug("Found device {} :: rssi={} avg={} status={}".format(mac, rssi, avg_rssi, status))
        ## note we use the actual value for enter, so we respond quickly
        ## and the average for exit so we don't get triggered early
        if rssi > -80 and status == 0:
            logging.debug("should be entering")
            logging.debug("{} using {} entering".format(g_devices[mac]["owner"], mac))
            write_fifo("enter", g_devices[mac]["owner"])
            os.system("sudo -u pi aplay ../sounds/enter.wav")
            status = 1
        elif avg_rssi < -75 and status == 1:
            logging.debug("should be exiting {}".format(avg_rssi))
            logging.debug("{} using {} exiting".format(g_devices[mac]["owner"], mac))
            write_fifo("exit", g_devices[mac]["owner"])
            os.system("sudo -u pi aplay ../sounds/exit.wav")
            status = 0
        if g_state[mac]['status'] != status:
            g_state[mac]['detected'] = time.time()
            g_state[mac]['status'] = status
            logging.debug("Found mac {} belonging to {} (RSSI: {}) [{},{:.0f}]".format(mac, g_devices[mac]["owner"], rssi, status, avg_rssi))
            logging.debug(g_state)

def check_for_missing():
    ## check to see if any devices have gone away
    for mac in g_state:
        if  mac in g_devices: # known device
            if "detected" in g_state[mac]:
                if g_state[mac]['status'] == 1:
                    duration = time.time() - g_state[mac]["detected"]
                    if duration > TIME_AWAY_IS_EXIT_IN_SECS:
                        logging.debug("exiting {}, time since {}".format(g_devices[mac]["owner"], duration))
                        g_state[mac]["status"] = 0
                        g_state[mac]['detected'] = time.time()
                        write_fifo("exit", g_devices[mac]["owner"])
                        os.system("sudo -u pi aplay ../sounds/exit.wav")

    logging.debug("function exit")

if __name__ == "__main__":
    root = logging.getLogger()
    root.setLevel(logging.DEBUG)
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('[%(asctime)s] [%(module)s::%(funcName)s] [%(levelname)s] %(message)s', datefmt="%Y-%m-%d %H:%M:%S")
    handler.setFormatter(formatter)
    root.addHandler(handler)

    if not os.geteuid() == 0:
        sys.exit("script only works as root or with sudo")

    btlib = find_library("bluetooth")
    if not btlib:
        raise Exception(
            "Can't find required bluetooth libraries"
            " (need to install bluez)"
        )
    bluez = CDLL(btlib, use_errno=True)

    # read devices from config file
    read_devices()
    read_state()

    g_ready = True

    # set handler to detect SIGUSR1 for reload
    signal.signal(signal.SIGINT, exit_request)
    signal.signal(signal.SIGUSR1, reload_request)

    result = start_scan_always()
    if result == False:
        logging.error("No bluetooth device found, exiting")
        os._exit(1)

    logging.debug("Starting main loop")
    write_fifo("start", "system")
    while True:
        # continue scan for 1 second
        if time.time() - g_timer > 5:
            logging.debug("about to stop scan")
            stop_scan()
            time.sleep(1)
            logging.debug("about to start scan")
            start_scan_always() # enters a loop waiting for the scan
        search_for_event()
        check_for_missing()
        if g_stop:
            break
    stop_scan()