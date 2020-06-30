import logging

from event import EventEnum, Event
from states.state import State


class EndState(State):
    """
    A default state that is added after the final configured state to return us to the first.
    Its ONLY job should be to link restart the context loop.
    """
    def __init__(self):
        super(EndState, self).__init__({}, {}, {})

    def on_enter(self):
        logging.debug("EndState::on_enter")
        if self._context:
            ev = Event(EventEnum.TRANSITION_TO_FIRST)
            self.context.add_event(ev)

    def on_exit(self):
        logging.debug("EndState::on_exit")

    def on_play_down(self):
        logging.debug("transitioning to new state")
        if self._context:
            ev = Event(EventEnum.TRANSITION_TO_FIRST)
            self.context.add_event(ev)


