import json
import logging
import os
import random
import signal
import threading
import time

from config_io import Configuration
from html_stripper import strip_tags
from states.continuous_state import ContinuousState
from states.state import State


class FactsState(ContinuousState):
    """
        Announcement interruption to main function

        Usages include making announcements to the user such as errors.

        Example:
        ev = Event(Event.INTERRUPT)
        state = AnnounceState(config, personality)
        state.message = "Something to say"
        ev.target_state = state
        context.do_interrupt(ev)

    """

    @staticmethod
    def create(configuration: Configuration, personality: "Personality", state_configuration):
        return FactsState(configuration, personality, state_configuration)


    def __init__(self,
                 configuration: Configuration,
                 personality: "Personality",
                 state_configuration=None
                 ) -> None:
        super(FactsState, self).__init__(configuration, personality, state_configuration)
        self.fact_id = None

    def random_fact(self):
        if not "filename" in self.state_config:
            return None
        full_path = os.path.join(self.configuration.get_config_path(), self.state_config["filename"])
        if os.path.isfile(full_path):
            with open(full_path, "r") as in_file:
                data = json.load(in_file)
            if self.fact_id is None:
                r = random.choice(data)
            else:
                r = self.pick(data, self.fact_id)
            logging.debug(r)
            text = strip_tags(r["fact"])
            return text
        return None

    def pick(self, data, id):
        for d in data:
            if d['id'] == id:
                return d
        return None

    def do_work_in_thread(self, is_first_run):
        message = self.random_fact()
        logging.debug(message)
        if message is not None:
            self.personality.voice_library.say(message, None, False)
        time.sleep(3)

