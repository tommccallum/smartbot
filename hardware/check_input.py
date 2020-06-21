"""
WORK IN PROGRESS

Check the device works by itself - may not be needed.
-TM 20/06/2020

"""
from evdev import ecodes, InputDevice, categorize, list_devices

name = "D0:8A:55:00:9C:27"

for path in list_devices():
    input_dev = InputDevice(path)
    if input_dev.name == name:
        device = path
    print("Found device " + name + " at " + device)
