import unittest
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__),"../src"))


from activities.announce_state import AnnounceState
from personality import Personality
from config_io import Configuration
import time

CURDIR=os.path.abspath(os.path.dirname(__file__))


class TestAnnounceState(unittest.TestCase):
    def test_play(self):
        config = Configuration()
        p = Personality(config)
        state = AnnounceState(config, p)
        state.message = "Testing announcement"
        state.on_enter();
        time.sleep(3)
        state.on_exit();


if __name__ == '__main__':
    unittest.main()
