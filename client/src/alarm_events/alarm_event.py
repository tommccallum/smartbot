import threading
import logging
import time

class AlarmEvent:
    """Base class for an Alarm event"""

    def __init__(self, data: object):
        self.data = data
        logging.debug(data)
        self.parent = None

    def validate(self):
        """
        called during setup of alarm
        Override to validate each different alarm action
        """
        return True

    def run(self, config):
        """
        DO NOT OVERRIDE

        run the code for the alarm action
        then this will continually call back until its finished and call on_finish when done
        """
        self.config = config
        logging.debug(self.data)
        self.begin_action()

    def is_finished(self):
        """
        DO NOT OVERRIDE
        Calls back every second to see if the alarm has finished
        Only call from the holder of this event
        """
        if self.parent is None:
            raise ValueError("no parent specified for alarm event")
        if self.test_is_finished():
            logging.debug("detected that alarm event has completed its action")
            self.on_finish()
            return True
        return False
        # if self.parent:
        #     self.parent.on_alarm_event_exit()


    def begin_action(self):
        """Override to start the event action"""
        pass

    def test_is_finished(self):
        """Override to test if alarm event has completed"""
        pass

    def on_finish(self):
        """Override to carry out clean up after end of event"""
        pass

    def exit(self):
        """called on exit of parent state"""
        pass

    def on_interrupt(self):
        pass

    def on_continue(self):
        pass

