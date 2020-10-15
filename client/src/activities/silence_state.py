import datetime
import logging

from actions import inline_action
from activities.activity import Activity
from event import EventEnum, Event


class SilenceState(Activity):
    """
    Used after sleep state, should not say or do anything
    """

    def __init__(self,
                 app_state,
                 state_configuration
                 ) -> None:
        super().__init__(app_state, state_configuration)
        self.title = "Silence"

    def on_enter(self):
        logging.debug("SilenceState::on_enter")

    def on_exit(self):
        logging.debug("SilenceState::on_exit")

    def say_time(self):
        saying = "The time is %T."
        saying = saying.replace("%T", datetime.datetime.now().strftime("%H:%M"))
        inline_action(saying)

    def say_prompt(self):
        inline_action("Hi Innogen")
        self.say_time()
        inline_action("I am currently waiting for something to do.  Use the play button to move to another activity.")

    def on_next_track_down(self):
        self.say_prompt()

    def on_previous_track_down(self):
        self.say_prompt()

    def on_play_down(self):
        logging.debug("transitioning to new state")
        if self._context:
            ev = Event(EventEnum.TRANSITION_TO_FIRST)
            self.add_event(ev)

