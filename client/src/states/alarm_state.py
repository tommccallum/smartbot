import glob
import json
import os
import re
import time
import logging

from event import Event
from states.state import State


class AlarmState(State):
    @staticmethod
    def create(configuration: "Configuration", personality: "Personality", state_configuration: object):
        """
        Optional
        state_configuration is expected to be the alarm event
        """
        return AlarmState(configuration, personality, state_configuration)

    def __init__(self,
                 configuration: "Configuration",
                 personality: "Personality",
                 state_configuration
                 ) -> None:
        super(AlarmState, self).__init__(configuration, personality, state_configuration)
        self.state_config.parent = self


    def notify(self, event: Event):
        if self.state_config is not None:
            self.state_config.notify(event);

    def on_enter(self):
        """on entering this new state"""
        logging.debug("alarm is starting")
        if self.state_config is not None:
            self.state_config.run(self.configuration)

    def on_exit(self):
        """on transitioning from this state"""
        logging.debug("alarm is exiting")
        if self.state_config is not None:
            self.state_config.exit()

    def on_interrupt(self):
        logging.debug("alarm was interrupted")
        if self.state_config is not None:
            self.state_config.on_interrupt()

    def on_continue(self):
        logging.debug("alarm was continuing after interrupt")
        if self.state_config is not None:
            self.state_config.on_continue()

    def is_finished(self):
        if self.state_config is not None:
            return self.state_config.is_finished()
        else:
            return True



