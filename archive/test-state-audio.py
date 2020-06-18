import unittest
import os

from archive.audio_state import AudioState
from personality import Personality
from config_io import Configuration
import time

CURDIR=os.path.abspath(os.path.dirname(__file__))


class TestAudioState(unittest.TestCase):
    def test_play(self):
        config = Configuration()
        p = Personality(config)
        state_config = {
            "name": "audio",
            "title": "Latest Programmes",
            "path": "%HOME%/Radio_Uncompressed/tmp",
            "extensions": "m4a",
            "orderby": ["date", "desc"]
        }
        state = AudioState.create(config, p, state_config)
        state.on_enter();
        time.sleep(3)
        state.on_exit();


if __name__ == '__main__':
    unittest.main()
