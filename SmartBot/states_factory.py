from config_io import Configuration
from handler_state import HandlerState
from states.audio_state import AudioState
from states.end_state import EndState
from states.live_stream_state import LiveStreamState
from states.introduction_state import IntroductionState

class StatesFactory:

    @staticmethod
    def create(configuration : Configuration, personality: "Personality") -> HandlerState:
        states = personality.json["states"]
        if len(states) == 0:
            raise ValueError("No personality states found.")
        first_object = None
        last_object = None
        for state in states:
            this_object = StatesFactory.map_object(state, configuration, personality)
            if not first_object:
                first_object = this_object
                last_object = first_object
            else:
                last_object.set_next_state(this_object)
            last_object = this_object
        last_object.set_next_state(EndState())
        return first_object

    @staticmethod
    def map_object(state, configuration : Configuration, personality : "Personality"):
        if not type(state) is dict:
            raise ValueError("state should be a dictionary")
        if not "name" in state:
            raise ValueError("state should have a name attribute")
        if state["name"].lower() == "live":
            return LiveStreamState.create(configuration, personality, state)
        elif state.name.lower() == "audio":
            return AudioState.create(configuration, personality, state)
        elif state.name.lower() == "introduction":
            return IntroductionState.create(configuration, personality, state)

