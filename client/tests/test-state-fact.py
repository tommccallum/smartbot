import logging
import unittest
import os
import sys


sys.path.insert(0, os.path.join(os.path.dirname(__file__),"../src"))

import globalvars
from states.facts_state import FactsState
from personality import Personality
from config_io import Configuration
import time
from main import init_application

CURDIR=os.path.abspath(os.path.dirname(__file__))


class TestFactState(unittest.TestCase):
    def test_play(self):
        init_application()
        state = FactsState(globalvars.app_context.config, globalvars.app_context.personality, { "type": "facts",
            "title": "Funky Facts",
            "filename":"facts_*.json",
            "on_enter": "Here are some funky facts.",
            "on_empty": "There are no funky facts available." })
        #state.fact_id="504788"
        state.on_enter()
        time.sleep(10)
        state.on_exit()
        logging.debug("wait")
        time.sleep(3)
        state.on_enter()
        time.sleep(10)
        state.on_exit()


if __name__ == '__main__':
    unittest.main()
