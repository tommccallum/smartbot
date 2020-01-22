from config_io import Configuration
from handler_state import HandlerState
from states.end_state import EndState
from states.live_stream_state import LiveStreamState


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
    def map_object(name, configuration : Configuration, personality : "Personality"):
        if name.lower() == "live_stream":
            return LiveStreamState.create(configuration, personality)