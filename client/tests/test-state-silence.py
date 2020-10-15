import unittest
import os
import sys


sys.path.insert(0, os.path.join(os.path.dirname(__file__),"../src"))

from activities.silence_state import SilenceState
from personality import Personality
from config_io import Configuration
import globalvars
from main import init_application

class TestSilenceState(unittest.TestCase):
    def test_say_prompt(self):
        init_application()
        c = globalvars.app_context.config
        p = globalvars.app_context.personality
        state = SilenceState.create(c, p, {})
        state.say_prompt()



if __name__ == '__main__':
    unittest.main()
