import logging

from actions import time_based_greeting
from activities.activity import Activity
from event import EventEnum, Event


class IntroductionState(Activity):
    """
    A default state that is added after the final configured state to return us to the first.
    Its ONLY job should be to link restart the context loop.
    """

    def __init__(self,
                 app_state,
                 state_configuration
                 ) -> None:
        super().__init__(app_state, state_configuration)
        self.next_track = 0
        self.first_run = True
        if "phrases" in self.state_config:
            self.phrases = self.state_config["phrases"]
        if "introduction" in self.json:
            self.first_run = self.json["introduction"]

    def on_enter(self):
        logging.debug("IntroductionState::on_enter")
        if self.first_run:
            self.app_state.voice_library.say("{} {}".format(time_based_greeting(), self.app_state.config().json["owner"]))
            if not self.json or not "introduction" in self.json:
                self.app_state.voice_library.say("My name is {}".format(self.app_state.personality.get_name()))
                self.json["introduction"] = True
            self._save()
            self.first_run = False

        ## we have to instruct the context owner to move to next step
        ## this is None if we are testing solo
        if self._context:
            ev = Event(EventEnum.TRANSITION_TO_NEXT)
            self.add_event(ev)


    def on_exit(self):
        logging.debug("IntroductionState::on_exit")

    def is_finished(self):
        return True