import logging

from activities.activity import Activity
from event import EventEnum, Event


class EndState(Activity):
    """
    A default state that is added after the final configured state to return us to the first.
    Its ONLY job should be to link restart the context loop.
    """
    def __init__(self, app_state, state_config):
        super().__init__(app_state, state_config)

    def on_enter(self):
        logging.debug("EndState::on_enter")
        ev = Event(EventEnum.TRANSITION_TO_FIRST)
        self.add_event(ev)

    def on_exit(self):
        logging.debug("EndState::on_exit")

    def on_play_down(self):
        logging.debug("transitioning to new state")
        ev = Event(EventEnum.TRANSITION_TO_FIRST)
        self.add_event(ev)


