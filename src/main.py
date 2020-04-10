#!/usr/bin/python3

from config_io import Configuration,create_config
from event_device_handler import EventDeviceAgent
from personality_io import Personality
from user_context import UserContext
import atexit
import os
import time

@atexit.register
def clean_exit():
    pass

def app_init():
    config = create_config()
    personality = Personality(config)
    states = personality.get_states()
    context = UserContext(states)
    context.personality = personality
    config.context = context
    return config, context


def start_event_device_agent(config, context):
    ev = EventDeviceAgent(config.get_device(), handler=context)
    try:
        ev.read_event()
    finally:
        ev.close()


if __name__ == "__main__":
    app_config, app_context = app_init()
    # begin listening to device events such as
    # vol up, vol down etc.
    # this should throw an exception if /dev/input/eventN location
    # is not found
    start_event_device_agent(app_config,app_context)
    # start main loop through states
    app_context.start()
    # scanner for LE bluetooth devices needs to run as root
    # so we listen to a FIFO for an indication of who's here
    while True:
        print("Reading Bluetooth LE devices")
        fifo_full_path = make_fifo("lescanner.fifo")
        with open( fifo_full_path, "r" ) as fifo:
            while line = fifo.read()
                if len(line) > 0:
                    (when, event, owner) = line.split(",")
                    print("[DEBUG] {} {} {}".format(when, event, owner)
#                    if event == "ENTER":
#                        app_context.on_owner_enter(owner, when)
#                    elif event == "EXIT":
#                        app_context.on_owner_exit(owner, when)
        # sleep the main process
        time.sleep(1)
