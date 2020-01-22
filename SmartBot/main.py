#!/usr/bin/python3

from config_io import Configuration
from event_device_handler import EventDeviceAgent
from personality_io import Personality
from user_context import UserContext

if __name__ == "__main__":
    config = Configuration()
    personality = Personality(config)
    states = personality.get_states()
    context = UserContext(states)
    ev = EventDeviceAgent(config.get_device(), handler=context)
    try:
        ev.read_event()
    finally:
        ev.close()
