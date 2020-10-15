import logging
import os
import signal

from activities.activity import Activity
from app_state import AppState


class AnnounceState(Activity):
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
    def __init__(self,
                 app_state: AppState,
                 state_configuration=None
                 ) -> None:
        super(AnnounceState, self).__init__(app_state, state_configuration)
        self.message = None

    def on_enter(self):
        """on entering this new state"""
        logging.debug("entering state")
        self.app_state.personality.voice_library.say(self.message)

    def on_exit(self):
        """on transitioning from this state"""
        logging.debug("exiting")

    def on_interrupt(self):
        logging.debug("interrupted")

    def on_continue(self):
        logging.debug("continuing")

    def is_finished(self):
        return True