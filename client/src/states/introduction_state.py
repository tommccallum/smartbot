import logging
import random

from actions import time_based_greeting
from config_io import Configuration
from event import EventEnum, Event
from states.state import State

class IntroductionState(State):
    """
    A default state that is added after the final configured state to return us to the first.
    Its ONLY job should be to link restart the context loop.
    """

    @staticmethod
    def create(configuration: Configuration, personality: "Personality", state_configuration):
        return IntroductionState(configuration, personality, state_configuration)

    def __init__(self,
                 configuration: Configuration,
                 personality: "Personality",
                 state_configuration
                 ) -> None:
        super(IntroductionState, self).__init__(configuration, personality, state_configuration)
        self.next_track = 0
        self.first_run = True
        if "phrases" in self.state_config:
            self.phrases = self.state_config["phrases"]
        if "introduction" in self.json:
            self.first_run = self.json["introduction"]

    def on_enter(self):
        logging.debug("IntroductionState::on_enter")
        if self.first_run:
            self.personality.voice_library.say("{} {}".format(time_based_greeting(), self.configuration.json["owner"]))
            if not self.json or not "introduction" in self.json:
                self.personality.voice_library.say("My name is {}".format(self.personality.get_name()))
                self.json["introduction"] = True
            self._save()
            self.first_run = False

        ## we have to instruct the context owner to move to next step
        ## this is None if we are testing solo
        if self._context:
            ev = Event(EventEnum.TRANSITION_TO_NEXT)
            self.context.add_event(ev)


    def on_exit(self):
        logging.debug("IntroductionState::on_exit")

    def is_finished(self):
        return True