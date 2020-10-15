import logging

from activities.activity import Activity
from app_state import AppState
from event import Event


class AlarmState(Activity):

    def __init__(self,
                 app_state: AppState,
                 state_configuration
                 ) -> None:
        super().__init__(app_state, state_configuration)
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



