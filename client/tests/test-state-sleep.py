import unittest
import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__),"../src"))

from main import init_application
import globalvars
from activities.sleep_state import SleepState


class TestSleepState(unittest.TestCase):
    # def test_press_anything(self):
    #     init_application()

    def test_music(self):
        init_application()
        state = SleepState.create(globalvars.app_context.config, globalvars.app_context.personality, {})
        print("first play")
        state.play_sleepy_music()
        time.sleep(10)
        print("pausing...")
        state.mplayer.pause()
        time.sleep(2)
        # should continue
        print("does this restart?")
        state.play_sleepy_music()
        time.sleep(5)
        print("Seeking to end")
        state.mplayer.seek(780)
        time.sleep(30)
        print("waiting to complete")
        while not state.mplayer.is_finished(): pass
        print("does this restart?")
        state.play_sleepy_music()
        time.sleep(30)



if __name__ == '__main__':
    unittest.main()
