import datetime
import os
import unittest
import time
import logging
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__),"../src"))

from config_io import Configuration
from personality import Personality
from states_factory import StatesFactory
from user_context import UserContext

CURDIR=os.path.abspath(os.path.dirname(__file__))

class TestAlarmInterruptFactory(unittest.TestCase):
    def test_alarm_interrupting_live_radio(self):
        config = Configuration()
        now = datetime.datetime.now()
        logging.debug(now)
        one_minute_from_now = now + datetime.timedelta(minutes=1)
        one_minute_from_now_str = one_minute_from_now.strftime("%H:%M")
        logging.debug(one_minute_from_now)
        logging.debug(one_minute_from_now_str)
        alarm_schedule = [
            {
                "when": [one_minute_from_now_str],
                "action": "play",
                "args": {
                    "track": CURDIR + "/../../sounds/piano2.m4a",
                    "run_once": True
                }
            }
        ]
        config.alarm.update_schedule(alarm_schedule)
        config.alarm.start()
        personality = Personality(config)
        personality.do_not_save = True
        states = [{
                "type": "audio",
                "title": "Live Radio",
                "filename": "live_stream.json",
                "on_enter": "You are now listening to live radio.",
                "on_empty": "There are no radio stations available."
            }
        ]
        personality.set_states(states)
        item = StatesFactory.create(config, personality)
        context = UserContext(item)
        config.context = context
        context.personality = personality
        config.context = context
        logging.debug("Starting state context")
        context.start()
        start_time = datetime.datetime.now()
        while True:
            context.update()
            time.sleep(0.5)
            # if not config.alarm.is_running():
            #     time.sleep(20)
            #     break
            if (datetime.datetime.now() - start_time).seconds > 90:
                break


if __name__ == '__main__':
    unittest.main()
