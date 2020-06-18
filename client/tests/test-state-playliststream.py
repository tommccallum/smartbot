import unittest
import os
import logging
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__),"../src"))

from personality import Personality
from config_io import Configuration
import time

from states.playlist_stream_state import PlaylistStreamState

CURDIR=os.path.abspath(os.path.dirname(__file__))


class TestPlaylistStreamState(unittest.TestCase):
    # def test_play(self):
    #     config = Configuration()
    #     p = Personality(config)
    #     state = PlaylistStreamState.create(config, p, {})
    #     state.on_enter()
    #     time.sleep(3)
    #     state.on_exit()
    #
    # def test_empty_list(self):
    #     config = Configuration()
    #     p = Personality(config)
    #     empty_playlist = {
    #         "type": "audio",
    #         "title": "Saved Programmes",
    #         "on_enter": "You are now listening to your favourites.",
    #         "on_empty": "There are no favourites chosen yet."
    #     }
    #     state = PlaylistStreamState.create(config, p, empty_playlist)
    #     state.on_enter();
    #     for attempt in range(0,2):
    #         time.sleep(3)
    #         logging.debug("attempting to move to next track in empty livestream")
    #         state.on_next_track_down()
    #         state.on_next_track_up()
    #     time.sleep(3)
    #     state.on_exit()

    # def test_checkpoint(self):
    #     config = Configuration()
    #     p = Personality(config)
    #     empty_playlist = {
    #         "type": "audio",
    #         "title": "Test Checkpoint",
    #         "filename": "checkpoint.json",
    #         "playlist": {
    #             "tracks": [
    #                 { "directory": "/home/pi/Radio_Uncompressed/tmp", "extensions": "m4a", "include-subdir": True }
    #             ],
    #             "orderby": ["date", "desc"]
    #         },
    #         "on_enter": "You are now listening to a test list.",
    #         "on_empty": "There are no favourites chosen yet."
    #     }
    #     state = PlaylistStreamState.create(config, p, empty_playlist)
    #     logging.debug("creating")
    #     print(state.json)
    #     logging.debug("on_enter")
    #     state.on_enter()
    #     print(state.json)
    #     for attempt in range(0,10):
    #         time.sleep(3)
    #         logging.debug("attempting to saving checkpoint")
    #         state.checkpoint()
    #         print(state.json)
    #     time.sleep(3)
    #     print(state.json)
    #     logging.debug("on_exit")
    #     state.on_exit()
    #     print(state.json)
    #
    #     logging.debug("*********** RESTARTING ************")
    #     logging.debug("on_enter")
    #     state.on_enter()
    #     print(state.json)
    #     time.sleep(10)
    #     state.on_exit()
    #     print(state.json)

    # def test_multiple_tracks(self):
    #     config = Configuration()
    #     p = Personality(config)
    #     empty_playlist = {
    #         "type": "audio",
    #         "title": "Test Checkpoint",
    #         "filename": "checkpoint.json",
    #         "playlist": {
    #             "tracks": [
    #                 { "directory": "/home/pi/Radio_Uncompressed/tmp", "extensions": "m4a", "include-subdir": True }
    #             ],
    #             "orderby": ["date", "desc"]
    #         },
    #         "on_enter": "You are now listening to a test list.",
    #         "on_empty": "There are no favourites chosen yet."
    #     }
    #     state = PlaylistStreamState.create(config, p, empty_playlist)
    #     logging.debug("creating")
    #     print(state.json)
    #
    #     ## test the _say_track messaging
    #     # track = state.get_next_track()
    #     # state._say_track(track, 0)  # 0 seconds
    #     # state._say_track(track, 45) # 45 seconds
    #     # state._say_track(track, 120) # 2 minutes
    #     # state._say_track(track, 123) # 2 minutes and 3 seconds
    #     # state._say_track(track, 2*60*60) # 2 hours
    #     # state._say_track(track, 2 * 60 * 60 + 34 * 60 )  # 2 hours and 34 minutes
    #     # state._say_track(track, 2 * 60 * 60 + 34 * 60 + 15)  # 2 hours 34 minutes and 15 seconds
    #
    #
    #     logging.debug("on_enter")
    #     state.on_enter()
    #     print(state.json)
    #     for attempt in range(0,10):
    #         time.sleep(3)
    #         logging.debug("attempting to saving checkpoint")
    #         state.checkpoint()
    #         print(state.json)
    #     logging.debug("next track 2 ")
    #     state.on_next_track_down()
    #     for attempt in range(0, 10):
    #         time.sleep(3)
    #         logging.debug("attempting to saving checkpoint")
    #         state.checkpoint()
    #         print(state.json)
    #     logging.debug("next track 3")
    #     state.on_next_track_down()
    #     for attempt in range(0, 10):
    #         time.sleep(3)
    #         logging.debug("attempting to saving checkpoint")
    #         state.checkpoint()
    #         print(state.json)
    #     logging.debug("next track 4")
    #     state.on_next_track_down()
    #     for attempt in range(0, 10):
    #         time.sleep(3)
    #         logging.debug("attempting to saving checkpoint")
    #         state.checkpoint()
    #         print(state.json)
    #     logging.debug("next track 1")
    #     state.on_next_track_down()
    #     for attempt in range(0, 10):
    #         time.sleep(3)
    #         logging.debug("attempting to saving checkpoint")
    #         state.checkpoint()
    #         print(state.json)
    #     logging.debug("next track")
    #     state.on_next_track_down()
    #
    #     time.sleep(3)
    #     print(state.json)
    #     logging.debug("on_exit")
    #     state.on_exit()
    #     print(state.json)
    #
    #
    #
    #     logging.debug("*********** RESTARTING ************")
    #     logging.debug("on_enter")
    #     state.on_enter()
    #     print(state.json)
    #     time.sleep(10)
    #     state.on_exit()
    #     print(state.json)

    def test_move_automatically_onto_next_track(self):
        config = Configuration()
        p = Personality(config)
        empty_playlist = {
            "type": "audio",
            "title": "Test progress",
            "filename": "checkpoint2.json",
            "playlist": {
                "tracks": [
                    { "directory": "/home/pi/Music/dance", "extensions": ["m4a","wav"], "include-subdir": True }
                ],
                "orderby": ["date", "desc"]
            },
            "on_enter": "You are now listening to a test list.",
            "on_empty": "There are no favourites chosen yet."
        }
        state = PlaylistStreamState.create(config, p, empty_playlist)
        logging.debug("creating")
        print(state.json)
        state.on_enter()
        time.sleep(15)
        state.is_finished()
        time.sleep(15)
        state.is_finished()
        time.sleep(15)
        print(state.json)

if __name__ == '__main__':
    unittest.main()
