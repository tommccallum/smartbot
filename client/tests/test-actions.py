import unittest
import os
import sys
from freezegun import freeze_time



sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../src"))

CURDIR = os.path.abspath(os.path.dirname(__file__))
from app_state import AppState
import actions
import globalvars
from local_logging import setup_logging

class TestActions(unittest.TestCase):

    def setUp(self) -> None:
        state = AppState.create_from_file(os.path.join(CURDIR,"test_conf_simple","config.json"))
        globalvars.app_state = state
        setup_logging()

    def test_expand_path(self):
        self.assertEqual("/home/pi",actions.expand_path("%HOME%"))
        self.assertEqual("/home/pi/smartbot/client/tests/test_conf_simple", actions.expand_path("%CONFIG%"))
        self.assertEqual("/home/pi/smartbot", actions.expand_path("%SMARTBOT%"))

    def test_replace_tags(self):
        self.assertEqual("hello Bob", actions.replace_tags("hello %O"))

    def test_blocking_play(self):
        actions.blocking_play("%SMARTBOT%/sounds/beep.wav")

    def test_blocking_play_2(self):
        actions.blocking_play("%SMARTBOT%/sounds/Marconi_Union-Weightless-sleepversion.mp3")

    def test_time_based_greeting(self):
        for ii in range(0,23):
            expected = "Morning"
            if ii == 0 : expected = "Hello"
            if ii == 1: expected = "Hello"
            if ii == 2: expected = "Morning"
            if ii == 3: expected = "Morning"
            if ii == 4: expected = "Morning"
            if ii == 5: expected = "Morning"
            if ii == 6: expected = "Morning"
            if ii == 7: expected = "Morning"
            if ii == 8: expected = "Morning"
            if ii == 9: expected = "Morning"
            if ii == 10: expected = "Morning"
            if ii == 11: expected = "Morning"
            if ii == 12: expected = "Afternoon"
            if ii == 13: expected = "Afternoon"
            if ii == 14: expected = "Afternoon"
            if ii == 15: expected = "Afternoon"
            if ii == 16: expected = "Hello"
            if ii == 17: expected = "Hello"
            if ii == 18: expected = "Evening"
            if ii == 19: expected = "Evening"
            if ii == 20: expected = "Evening"
            if ii == 21: expected = "Evening"
            if ii == 22: expected = "Evening"
            if ii == 23: expected = "Evening"
            with freeze_time("2020-07-03 {:02d}:00:00".format(ii)):
                actual = actions.time_based_greeting()
                self.assertEqual(expected, actual)

    def test_inline_action(self):
        self.assertTrue(actions.inline_action("hello"))

    def test_inline_action_2(self):
        self.assertTrue(actions.inline_action({ "type": "speech", "text": "hello two" } ))

    def test_inline_action_3(self):
        self.assertTrue(actions.inline_action({ "type": "sound", "path": "%SMARTBOT%/sounds/piano2.m4a" } ))

    def test_inline_action_4(self):
        #emits warning log
        self.assertFalse(actions.inline_action({ "type": "sound", "wrong": "%SMARTBOT%/sounds/piano2.m4a" } ))

if __name__ == '__main__':
    unittest.main()
