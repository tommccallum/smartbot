import unittest
import os
import logging
from states.live_stream_state import LiveStreamState
from personality import Personality
from config_io import Configuration
import time

CURDIR=os.path.abspath(os.path.dirname(__file__))


class TestLiveStreamState(unittest.TestCase):
    def test_play(self):
        config = Configuration()
        p = Personality(config)
        state = LiveStreamState.create(config, p, {})
        state.on_enter();
        time.sleep(3)
        state.on_exit();

    def test_empty_list(self):
        config = Configuration()
        p = Personality(config)
        state = LiveStreamState.create(config, p, {})
        empty_playlist = {
            "playlist": []
        }
        state.json = empty_playlist
        state.on_enter();
        for attempt in range(0,2):
            time.sleep(3)
            logging.debug("attempting to move to next track in empty livestream")
            state.on_next_track_down()
            state.on_next_track_up()
        time.sleep(3)
        state.on_exit();

if __name__ == '__main__':
    unittest.main()
