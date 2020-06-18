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

class TestStateFactoryAll(unittest.TestCase):
    def test_load_states(self):
        config = Configuration()
        personality = Personality(config)
        personality.do_not_save = True
        item = StatesFactory.create(config, personality)
        context = UserContext(item)
        context.personality = personality
        config.context = context
        logging.debug("Starting state context")
        context.start()
        for ii in range(0,len(personality.json["states"])):
            time.sleep(3)
            logging.debug("*************  Next state context {}".format(ii))
            context.on_play_down()
            context.on_play_up()
        time.sleep(3)


if __name__ == '__main__':
    unittest.main()
