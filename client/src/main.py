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
event_device_agent = None

@atexit.register
def clean_exit():
    logging.debug("clean exit")
    # the above will send to the current state but not the rest
    # so we also loop through to ensure everything shutsdown cleaning
    if event_device_agent:
        event_device_agent.stop()
    if globalvars.app_context:
        globalvars.app_context.stop()
    logging.debug("making terminal sane again")
    if terminal_old_settings:
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, terminal_old_settings)



def app_init(config_path=None):
    config = Configuration(config_path)
    personality = Personality(config)
    states = personality.get_states()
    context = UserContext(states)
    context.personality = personality
    fifo_full_path = make_fifo(config, "lescanner.fifo")
    context.bluetooth_event_fifo = fifo_full_path
    config.context = context
    return config, context


def start_event_device_agent(config, context):
    global event_device_agent
    try:
        event_device_agent = EventDeviceAgent(context, config.get_device())
        event_device_agent.start()
    except Exception as e:
        logging.debug(e)
        if event_device_agent is not None:
            logging.debug("closing EventDeviceAgent")
            event_device_agent.close()
        event_device_agent = None


class MainListener:
    """Hack class to get working"""
    def __init__(self, config, context):
        self.config = config
        self.personality = context.personality
        self.context = context

    def notify(self, event):
        logging.debug("Received event {}".format(event))
        if event.id == EventEnum.ENTER_OWNER:
            self.on_enter_owner(event)
        if event.id == EventEnum.EXIT_OWNER:
            self.on_exit_owner(event)
        if event.id == EventEnum.DEVICE_FOUND:
            self.on_device_found(event)
        if event.id == EventEnum.DEVICE_LOST:
            self.on_device_lost(event)

    def on_enter_owner(self, ev):
        logging.debug("here")

    def on_exit_owner(self, ev):
        logging.debug("here")


    def on_device_found(self, ev):
        logging.debug("here")

    def on_device_lost(self, ev):
        logging.debug("here")


if __name__ == "__main__":
    #
    # Setup logging to both a file and to stdout
    #

    #!!!! SEE Configuration object
    # create log directory if it does not exist
    # log_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), "../log")
    # if os.path.isdir(log_path):
    #     os.mkdir(log_path)
    # log_file_name = "smartbot"
    #
    # logFormatter = logging.Formatter("[%(asctime)s] [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s")
    #
    # rootLogger = logging.getLogger()
    # fileHandler = logging.FileHandler("{0}/{1}.log".format(log_path, log_file_name))
    # fileHandler.setFormatter(logFormatter)
    # rootLogger.addHandler(fileHandler)
    #
    # consoleHandler = logging.StreamHandler(sys.stdout)
    # consoleHandler.setFormatter(logFormatter)
    # rootLogger.addHandler(consoleHandler)

    #
    # Main App
    #
    terminal_old_settings = termios.tcgetattr(sys.stdin)
    app_config, local_context = app_init()
    globalvars.app_context = local_context
    globalvars.app_context._listeners.append(MainListener(app_config, globalvars.app_context))

    # begin listening to device events such as
    # vol up, vol down etc.
    # this should throw an exception if /dev/input/eventN location
    # is not found
    start_event_device_agent(app_config,globalvars.app_context)
    # start listening to bluetooth events
    # read_fifo_in_thread(app_context.bluetooth_event_fifo, app_context)
    # start main loop through states
    globalvars.app_context.start()
    app_config.alarm.start();
    # scanner for LE bluetooth devices needs to run as root
    # so we listen to a FIFO for an indication of who's here
    while True:
        #logging.debug("listening")
        if not globalvars.app_context.update():
            break
        # sleep the main process
        time.sleep(0.25)
    # when this loop exit then the atexit.register function will be called