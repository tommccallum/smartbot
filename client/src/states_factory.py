import logging

from config_io import Configuration
from states.end_state import EndState
from states.facts_state import FactsState
from states.introduction_state import IntroductionState
from states.playlist_stream_state import PlaylistStreamState
from states.speaking_clock import SpeakingClockState
from states.state import State


class StatesFactory:
    """Creates a 'state' which is like a mode for the device
        each mode may have different uses for each of the 3 buttons on the bluetooth speaker
    """

    @staticmethod
    def create(configuration: Configuration, personality: "Personality") -> State:
        """

            Creates the set of user functionality that has been configured in personality.states
            Each 'State' is passed its own configuration from the file, this is called the state_configuration.
            It also needs the main configuration and personality profile.
        """
        states = personality.json["states"]
        state_objects = []
        if len(states) == 0:
            raise ValueError("No personality states found.")
        for state in states:
            this_object = StatesFactory.map_object(state, configuration, personality)
            state_objects.append(this_object)
        state_objects.append(EndState())
        return state_objects

    @staticmethod
    def map_object(state, configuration: Configuration, personality: "Personality"):
        if not type(state) is dict:
            logging.debug("state should be a dictionary")
            logging.debug(state)
            raise ValueError("state should be a dictionary")
        if not "type" in state:
            logging.debug("state should have a type attribute")
            logging.debug(state)
            raise ValueError("state should have a type attribute")
        if not "title" in state:
            state["title"] = state["type"]

        logging.debug("Creating {} state {}".format(state['type'], state["title"]))
        logging.debug(state)
        if state["type"].lower() == "audio":
            return PlaylistStreamState.create(configuration, personality, state)
        elif state["type"].lower() == "introduction":
            return IntroductionState.create(configuration, personality, state)
        elif state["type"].lower() == "speakingclock":
            return SpeakingClockState.create(configuration, personality, state)
        elif state["type"].lower() == "facts":
            return FactsState.create(configuration, personality, state)
