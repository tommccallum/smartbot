#!/usr/bin/python3

from config_io import Configuration, create_config
from event_device_handler import EventDeviceAgent
from personality_io import Personality
from user_context import UserContext


def app_init():
    config = create_config()
    personality = Personality(config)
    states = personality.get_states()
    context = UserContext(states)
    config.context = context
    return config, context


def app_main_loop(config, context):
    ev = EventDeviceAgent(config.get_device(), handler=context)
    try:
        ev.read_event()
    finally:
        ev.close()


if __name__ == "__main__":
    app_config, app_context = app_init()
    app_main_loop(app_config,app_context)
