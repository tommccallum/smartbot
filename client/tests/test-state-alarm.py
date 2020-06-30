import logging
import unittest
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__),"../src"))


from personality import Personality
from config_io import Configuration
import datetime
import time

CURDIR=os.path.abspath(os.path.dirname(__file__))


class TestAlarmState(unittest.TestCase):
    def test_play(self):
        """Test the alarm by itself"""
        config = Configuration()
        p = Personality(config)
        now = datetime.datetime.now()
        logging.debug(now)
        one_minute_from_now = now + datetime.timedelta(minutes=1)
        one_minute_from_now_str = one_minute_from_now.strftime("%H:%M")
        logging.debug(one_minute_from_now)
        logging.debug(one_minute_from_now_str)
        alarm_schedule = [
            {
                "when": [ one_minute_from_now_str ],
                "action": "play",
                "args": {
                    "track": CURDIR+"/../../sounds/piano2.m4a",
                    "run_once": True
                }
            }
        ]
        config.alarm.update_schedule(alarm_schedule)
        config.alarm.start()
        logging.debug("please wait, while we test the alarm")
        time.sleep(90)
        # you should here the piano sound during this test

if __name__ == '__main__':
    unittest.main()
