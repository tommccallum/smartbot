import unittest
import os
import unittest
import sys
import time


sys.path.insert(0, os.path.join(os.path.dirname(__file__),"../src"))

CURDIR=os.path.abspath(os.path.dirname(__file__))

import globalvars
from local_logging import setup_logging
from skills.mplayer_process import MPlayerProcess
from app_state import AppState


class TestMPlayerProcess(unittest.TestCase):

    # def test_mplayer_process(self):
    #     setup_logging()
    #     mplayer_config_path = os.path.join(CURDIR,"test_conf_simple", "mplayer.json")
    #     test_config = os.path.join(CURDIR, "test_conf_simple", "config.json")
    #     globalvars.app_state = AppState.create_from_file(test_config)
    #     fifo_directory="/home/pi/.config/smartbot/fifos"
    #     track="/home/pi/smartbot/sounds/Marconi_Union-Weightless.mp3"
    #     seek=10
    #     player = MPlayerProcess(mplayer_config_path, fifo_directory)
    #     self.assertFalse(player.has_track_completed())
    #     player.play(track, seek)
    #     self.assertFalse(player.has_track_completed())
    #     player.stop()
    #     self.assertFalse(player.has_track_completed())
    #     self.assertEqual(15,player.get_duration())
    #     time.sleep(5)
    #     player.resume()
    #     self.assertFalse(player.has_track_completed())
    #     self.assertTrue(os.path.exists(player.fifo.full_path))
    #     self.assertIsNotNone(player.process)
    #     time.sleep(2)
    #     self.assertEqual(17, player.get_duration())
    #     player = None
        # should die

    def test_mplayer_process_completes(self):
        setup_logging()
        mplayer_config_path = os.path.join(CURDIR,"test_conf_simple", "mplayer.json")
        test_config = os.path.join(CURDIR, "test_conf_simple", "config.json")
        globalvars.app_state = AppState.create_from_file(test_config)
        fifo_directory="/home/pi/.config/smartbot/fifos"
        track="/home/pi/smartbot/sounds/piano2.m4a"
        seek=0 # this track is 6 seconds long
        player = MPlayerProcess(mplayer_config_path, fifo_directory)
        self.assertFalse(player.has_track_completed())
        player.play(track, seek)
        print(player.timer.elapsedTime())
        self.assertFalse(player.has_track_completed())
        print(player.timer.elapsedTime())
        time.sleep(2)
        print(player.timer.elapsedTime())
        self.assertFalse(player._is_alive())
        print(player.timer.elapsedTime())
        self.assertTrue(player.has_track_completed())
        print(player.timer.elapsedTime())
        self.assertEqual(7,player.get_duration())
        player = None
        # should die

if __name__ == '__main__':
    unittest.main()
