#!/usr/bin/python3

import atexit
import os
import termios
import time
import logging
import sys

from config_io import Configuration
from event_device_handler import EventDeviceAgent
from personality import Personality
from user_context import UserContext
from fifo import make_fifo, read_fifo_in_thread
from event import EventEnum, Event
import globalvars

global app_context
terminal_old_settings = None
app_config = None

@atexit.register
def clean_exit():
    logging.info("exiting application...")
    if globalvars.app_context:
        globalvars.app_context.stop()
    if terminal_old_settings:
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, terminal_old_settings)

def init_application(config_path=None):
    """
    Set up the 3 main classes: Configuration, Personality and Context
    This should be something that we can setup a unit test with
    :param config_path:
    :return:
    """
    global app_config
    global terminal_old_settings
    terminal_old_settings = termios.tcgetattr(sys.stdin)

    app_config = Configuration(config_path)
    personality = Personality(app_config)
    states = personality.get_states()
    context = UserContext(states, app_config, personality)
    app_config.context = context
    globalvars.app_context = context
    # globalvars.app_context._listeners.append(MainListener(app_config, globalvars.app_context))


def start_event_device_agent(config, context):
    if not config.bluetooth_speaker_capability:
        return
    try:
        event_device_agent = EventDeviceAgent(context, config.get_device())
        event_device_agent.start()
    except Exception as e:
        logging.debug("*** AAAH *** ")
        logging.debug(e)
        if event_device_agent is not None:
            logging.debug("closing EventDeviceAgent")
            event_device_agent.close()
        event_device_agent = None
    finally:
        globalvars.app_context.event_device_agent = event_device_agent


# class MainListener:
#     """Hack class to get working"""
#     def __init__(self, config, context):
#         self.config = config
#         self.personality = context.personality
#         self.context = context
#
#     def notify(self, event):
#         logging.debug("Received event {}".format(event))
#         if event.id == EventEnum.ENTER_OWNER:
#             self.on_enter_owner(event)
#         if event.id == EventEnum.EXIT_OWNER:
#             self.on_exit_owner(event)
#         if event.id == EventEnum.DEVICE_FOUND:
#             self.on_device_found(event)
#         if event.id == EventEnum.DEVICE_LOST:
#             self.on_device_lost(event)
#
#     def on_enter_owner(self, ev):
#         logging.debug("here")
#
#     def on_exit_owner(self, ev):
#         logging.debug("here")
#
#
#     def on_device_found(self, ev):
#         logging.debug("here")
#
#     def on_device_lost(self, ev):
#         logging.debug("here")


if __name__ == "__main__":
    #
    # Main App
    #
    init_application()

    # start main loop through states
    globalvars.app_context.start()

    # begin listening to device events such as
    # vol up, vol down etc.
    # this should throw an exception if /dev/input/eventN location is not found
    # this should not be part of init_application
    start_event_device_agent(app_config,globalvars.app_context)
    # start listening to bluetooth events
    # @UNCOMMENT WHEN READY TO TEST
    # read_fifo_in_thread(app_context.bluetooth_event_fifo, app_context)
    app_config.alarm.start();
    globalvars.app_context.main_loop()