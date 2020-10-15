import datetime
import unittest
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__),"../src"))


from activities.speaking_clock import SpeakingClockState
from personality import Personality
from config_io import Configuration
import time

CURDIR=os.path.abspath(os.path.dirname(__file__))


class TestSpeakingClockState(unittest.TestCase):
    def test_play(self):
        config = Configuration()
        p = Personality(config)
        state = SpeakingClockState(config, p)
        state.on_enter();
        time.sleep(12)
        state.on_exit();

    def test_morning(self):
        config = Configuration()
        p = Personality(config)
        state = SpeakingClockState(config, p)
        when = datetime.datetime.today()
        state.tell(when.replace(hour=10,minute=4))

    def test_afternoon(self):
        config = Configuration()
        p = Personality(config)
        state = SpeakingClockState(config, p)
        when = datetime.datetime.today()
        state.tell(when.replace(hour=16,minute=6))

    def test_evening(self):
        config = Configuration()
        p = Personality(config)
        state = SpeakingClockState(config, p)
        when = datetime.datetime.today()
        state.tell(when.replace(hour=19,minute=23))

    def test_night(self):
        config = Configuration()
        p = Personality(config)
        state = SpeakingClockState(config, p)
        when = datetime.datetime.today()
        state.tell(when.replace(hour=22,minute=45))

    def test_midday(self):
        config = Configuration()
        p = Personality(config)
        state = SpeakingClockState(config, p)
        when = datetime.datetime.today()
        state.tell(when.replace(day=1,hour=12,minute=00))

    def test_midnight(self):
        config = Configuration()
        p = Personality(config)
        state = SpeakingClockState(config, p)
        when = datetime.datetime.today()
        state.tell(when.replace(day=2,hour=0,minute=0))


    def test_midday_2(self):
        config = Configuration()
        p = Personality(config)
        state = SpeakingClockState(config, p)
        when = datetime.datetime.today()
        state.tell(when.replace(day=3,hour=12,minute=13))

    def test_midday_3(self):
        config = Configuration()
        p = Personality(config)
        state = SpeakingClockState(config, p)
        when = datetime.datetime.today()
        state.tell(when.replace(day=4,hour=12,minute=54))

    def test_midnight_2(self):
        config = Configuration()
        p = Personality(config)
        state = SpeakingClockState(config, p)
        when = datetime.datetime.today()
        state.tell(when.replace(month=1,day=31,hour=0,minute=4))

    def test_midnight_3(self):
        config = Configuration()
        p = Personality(config)
        state = SpeakingClockState(config, p)
        when = datetime.datetime.today()
        state.tell(when.replace(hour=0,minute=54))



if __name__ == '__main__':
    unittest.main()
