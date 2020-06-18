import unittest
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__),"../src"))

from personality import Personality
from config_io import Configuration
import time

from states.end_state import EndState

CURDIR=os.path.abspath(os.path.dirname(__file__))


class TestEndState(unittest.TestCase):
    def test_play(self):
        config = Configuration()
        p = Personality(config)
        state = EndState()
        state.on_enter();
        time.sleep(3)
        state.on_exit();


if __name__ == '__main__':
    unittest.main()
