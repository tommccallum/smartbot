import unittest
import os
import unittest
import sys
import time
from unittest.mock import patch



sys.path.insert(0, os.path.join(os.path.dirname(__file__),"../src"))

CURDIR=os.path.abspath(os.path.dirname(__file__))

from app_state import AppState
from skills.audio_player import AudioPlayer
from local_logging import setup_logging
import globalvars

class TestAudioPlayer1(unittest.TestCase):
    # def test_creation_and_deletion( self ):
    #     setup_logging()
    #     test_config = os.path.join(CURDIR, "test_conf_simple", "config.json")
    #     app_state = AppState.create_from_file(test_config)
    #     audio = AudioPlayer(app_state)

    # def test_play(self):
    #     setup_logging()
    #     test_config = os.path.join(CURDIR, "test_conf_simple", "config.json")
    #     globalvars.app_state = AppState.create_from_file(test_config)
    #     audio = AudioPlayer(globalvars.app_state)
    #     track = "/home/pi/smartbot/sounds/Marconi_Union-Weightless.mp3"
    #     seek = 10
    #     self.assertTrue(audio.is_stopped())
    #     self.assertFalse(audio.is_paused())
    #     self.assertFalse(audio.is_playing())
    #     self.assertFalse(audio.has_track_completed())
    #     audio.play(track,seek)
    #     self.assertFalse(audio.is_stopped())
    #     self.assertTrue(audio.is_playing())
    #     self.assertFalse(audio.is_paused())
    #     self.assertFalse(audio.has_track_completed())
    #     time.sleep(2)
    #     audio.pause()
    #     self.assertFalse(audio.is_stopped())
    #     self.assertFalse(audio.is_playing())
    #     self.assertTrue(audio.is_paused())
    #     self.assertFalse(audio.has_track_completed())
    #     time.sleep(2)
    #     audio.resume()
    #     self.assertFalse(audio.is_stopped())
    #     self.assertTrue(audio.is_playing())
    #     self.assertFalse(audio.is_paused())
    #     self.assertFalse(audio.has_track_completed())
    #     time.sleep(2)
    #     audio.stop()
    #     self.assertTrue(audio.is_stopped())
    #     self.assertFalse(audio.is_playing())
    #     self.assertFalse(audio.is_paused())
    #     self.assertFalse(audio.has_track_completed())

    # def test_play_2(self):
    #     setup_logging()
    #     test_config = os.path.join(CURDIR, "test_conf_simple", "config.json")
    #     globalvars.app_state = AppState.create_from_file(test_config)
    #     audio = AudioPlayer(globalvars.app_state)
    #     track = "/home/pi/smartbot/sounds/Marconi_Union-Weightless.mp3"
    #     seek = 10
    #     self.assertTrue(audio.is_stopped())
    #     self.assertFalse(audio.is_paused())
    #     self.assertFalse(audio.is_playing())
    #     self.assertFalse(audio.has_track_completed())
    #     audio.play(track,seek)
    #     self.assertFalse(audio.is_stopped())
    #     self.assertTrue(audio.is_playing())
    #     self.assertFalse(audio.is_paused())
    #     self.assertFalse(audio.has_track_completed())
    #     time.sleep(2)
    #     audio.on_interrupt()
    #     self.assertFalse(audio.is_stopped())
    #     self.assertFalse(audio.is_playing())
    #     self.assertTrue(audio.is_paused())
    #     self.assertFalse(audio.has_track_completed())
    #     time.sleep(2)
    #     audio.on_continue()
    #     self.assertFalse(audio.is_stopped())
    #     self.assertTrue(audio.is_playing())
    #     self.assertFalse(audio.is_paused())
    #     self.assertFalse(audio.has_track_completed())
    #     time.sleep(2)
    #     audio.stop()
    #     self.assertTrue(audio.is_stopped())
    #     self.assertFalse(audio.is_playing())
    #     self.assertFalse(audio.is_paused())
    #     self.assertFalse(audio.has_track_completed())

    # def test_play_intertwined_pass(self):
    #     setup_logging()
    #     test_config = os.path.join(CURDIR, "test_conf_simple", "config.json")
    #     globalvars.app_state = AppState.create_from_file(test_config)
    #     audio = AudioPlayer(globalvars.app_state)
    #     track = "/home/pi/smartbot/sounds/Marconi_Union-Weightless.mp3"
    #     seek = 10
    #     audio2 = AudioPlayer(globalvars.app_state)
    #     track2 = "/home/pi/smartbot/sounds/Marconi_Union-Weightless.mp3"
    #     seek2 = 60
    #
    #     self.assertTrue(audio.is_stopped())
    #     self.assertFalse(audio.is_paused())
    #     self.assertFalse(audio.is_playing())
    #     self.assertFalse(audio.has_track_completed())
    #     audio.play(track,seek)
    #     self.assertFalse(audio.is_stopped())
    #     self.assertTrue(audio.is_playing())
    #     self.assertFalse(audio.is_paused())
    #     self.assertFalse(audio.has_track_completed())
    #     time.sleep(2)
    #     audio.pause()
    #     audio2.play(track2,seek2)
    #     self.assertFalse(audio.is_stopped())
    #     self.assertFalse(audio.is_playing())
    #     self.assertTrue(audio.is_paused())
    #     self.assertFalse(audio.has_track_completed())
    #     time.sleep(5)
    #     audio2.pause()
    #     audio.resume()
    #     self.assertFalse(audio.is_stopped())
    #     self.assertTrue(audio.is_playing())
    #     self.assertFalse(audio.is_paused())
    #     self.assertFalse(audio.has_track_completed())
    #     time.sleep(5)
    #     audio.stop()
    #     self.assertTrue(audio.is_stopped())
    #     self.assertFalse(audio.is_playing())
    #     self.assertFalse(audio.is_paused())
    #     self.assertFalse(audio.has_track_completed())
    #     audio2.stop()


    # def test_play_intertwined_fail(self):
    #     setup_logging()
    #     test_config = os.path.join(CURDIR, "test_conf_simple", "config.json")
    #     globalvars.app_state = AppState.create_from_file(test_config)
    #     audio = AudioPlayer(globalvars.app_state)
    #     track = "/home/pi/smartbot/sounds/Marconi_Union-Weightless.mp3"
    #     seek = 10
    #     audio2 = AudioPlayer(globalvars.app_state)
    #     track2 = "/home/pi/smartbot/sounds/Marconi_Union-Weightless.mp3"
    #     seek2 = 60
    #
    #     audio2.play(track2, seek2)
    #     self.assertRaises(ValueError, audio.play, track,seek)

    def test_play_intertwined_fail_2(self):
        setup_logging()
        test_config = os.path.join(CURDIR, "test_conf_simple", "config.json")
        globalvars.app_state = AppState.create_from_file(test_config)
        audio = AudioPlayer(globalvars.app_state)
        track = "/home/pi/smartbot/sounds/Marconi_Union-Weightless.mp3"
        seek = 10
        audio2 = AudioPlayer(globalvars.app_state)
        track2 = "/home/pi/smartbot/sounds/Marconi_Union-Weightless.mp3"
        seek2 = 60

        audio.play(track2, seek2)
        self.assertRaises(ValueError, audio2.play, track,seek)

    def tearDown(self):
        globalvars.app_state = None


if __name__ == '__main__':
    unittest.main()
