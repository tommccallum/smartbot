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

class TestStateFactory(unittest.TestCase):
    def test_load_states(self):
        config = Configuration()
        personality = Personality(config)
        personality.do_not_save = True
        states = [{
            "name": "introduction"
            },{
                "type": "audio",
                "title": "Live Radio",
                "filename": "live_stream.json",
                "on_enter": "You are now listening to live radio.",
                "on_empty": "There are no radio stations available."
            }, {
                "type": "audio",
                "title": "Saved Programmes",
                "playlist": {
                    "tracks": [
                        { "directory": "%HOME%/Radio_Uncompressed/keep", "extensions": "m4a", "include-subdir": True }
                    ],
                    "orderby": "name"
                },
                "on_enter": "You are now listening to your favourites.",
                "on_empty": "There are no favourites chosen yet."
            },
            {
                "type": "audio",
                "title": "Latest Programmes",
                "playlist": {
                    "tracks": [
                        { "directory": "%HOME%/Radio_Uncompressed/tmp", "extensions": "m4a", "include-subdir": True }
                    ],
                    "orderby": ["date", "desc"]
                },
                "on_enter": "You are now listening to the latest programmes.",
                "on_empty": "There are no programmes downloaded yet."
            }
        ]
        personality.set_states(states)
        item = StatesFactory.create(config, personality)
        context = UserContext(item)
        context.personality = personality
        config.context = context
        logging.debug("Starting state context")
        context.start()
        for ii in range(0,4):
            time.sleep(3)
            logging.debug("*************  Next state context {}".format(ii))
            context.on_play_down()
            context.on_play_up()
        ## change mode
        # for ii in range(0,6):
        #     time.sleep(3)
        #     logging.debug("*************  Next state context {}".format(ii))
        #     context.on_play_down()
        #     context.on_play_up()

        # ## change track
        # for ii in range(0, 3):
        #     time.sleep(3)
        #     logging.debug("Next track {}".format(ii))
        #     context.on_next_track_down()
        #     context.on_next_track_up()
        #
        #     ## change track
        #     for ii in range(0, 3):
        #         time.sleep(3)
        #         logging.debug("Pausing context {}".format(ii))
        #         context.on_previous_track_down()
        #         context.on_previous_track_up()


if __name__ == '__main__':
    unittest.main()
