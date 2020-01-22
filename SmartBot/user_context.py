from ability import Ability
from bluetooth_speaker_handler import BluetoothSpeakerHandler
from handler_state import HandlerState


class UserContext(BluetoothSpeakerHandler):
    """Main interface to client"""


    """Reference to the current state"""
    def __init__(self, state: HandlerState) -> None:
        self.queue = []
        self._state = None
        self._first = state
        self.transition_to(state)

    def transition_to_first(self):
        self.transition_to(self._first)

    def transition_to(self, state: HandlerState):
        if not state:
            state = self._first
        if self._state:
            self._state.on_exit()
        self._state = state
        self._state.context = self
        self._state.on_enter()

    def add(self, output : Ability) -> None:
        output.user_context = self
        self.queue.append(output)

    def execute(self) -> None:
        for out in self.queue:
            out.perform()
        self.queue = []

    def on_previous_track_down(self):
        self._state.on_previous_track_down()

    def on_previous_track_up(self):
        self._state.on_previous_track_up()

    def on_next_track_down(self):
        self._state.on_next_track_down()

    def on_next_track_up(self):
        self._state.on_next_track_up()

    def on_play_down(self):
        self._state.on_play_down()

    def on_play_up(self):
        self._state.on_play_up()