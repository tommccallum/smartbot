import unittest
import os
import logging
import sys


sys.path.insert(0, os.path.join(os.path.dirname(__file__),"../src"))

from personality_settings import PersonalitySettings
from app_settings import AppSettings
from voice_library import VoiceLibrary


class TestVoiceLibrary(unittest.TestCase):
    def test_say_seconds(self):
        config = AppSettings.create()
        p = PersonalitySettings.create(config.get_personality_path())
        v = VoiceLibrary(config, p)
        self.assertEqual("", v.convert_seconds_to_saying(0))  # 0 seconds
        self.assertEqual("1 second", v.convert_seconds_to_saying(1))  # 45 seconds
        self.assertEqual("45 seconds", v.convert_seconds_to_saying(45)) # 45 seconds
        self.assertEqual("1 minute", v.convert_seconds_to_saying(60))  # 2 minutes
        self.assertEqual("2 minutes", v.convert_seconds_to_saying(120)) # 2 minutes
        self.assertEqual("2 minutes and 3 seconds", v.convert_seconds_to_saying(123)) # 2 minutes and 3 seconds
        self.assertEqual("1 hour", v.convert_seconds_to_saying(1 * 60 * 60))  # 1 hour
        self.assertEqual("2 hours", v.convert_seconds_to_saying(2*60*60)) # 2 hours
        self.assertEqual("2 hours and 1 minute", v.convert_seconds_to_saying(2 * 60 * 60 + 60))  # 2 hours
        self.assertEqual("2 hours and 34 minutes", v.convert_seconds_to_saying(2 * 60 * 60 + 34 * 60 ))  # 2 hours and 34 minutes
        self.assertEqual("2 hours 1 minute and 1 second", v.convert_seconds_to_saying(2 * 60 * 60 + 60+ 1))  # 2 hours
        self.assertEqual("2 hours 34 minutes and 15 seconds", v.convert_seconds_to_saying(2 * 60 * 60 + 34 * 60 + 15))  # 2 hours 34 minutes and 15 seconds
        self.assertEqual("2 hours and 15 seconds",v.convert_seconds_to_saying(2 * 60 * 60 +  15))  # 2 hours 34 minutes and 15 seconds

    def test_say_and_dont_save(self):
        config = AppSettings.create()
        p = PersonalitySettings.create(config.get_personality_path())
        v = VoiceLibrary(config, p)
        v.say("testing say", None, False)

    def test_say_and_save(self):
        config = AppSettings.create()
        p = PersonalitySettings.create(config.get_personality_path())
        v = VoiceLibrary(config, p)
        v.say("testing say", None, True)
        item = v.get_saying("testing say")
        print(item)
        self.assertIn("file_path", item)
        self.assertTrue(os.path.isfile(item["file_path"]))
        self.assertIn("keep_while_exists", item)
        self.assertIsNone(item["keep_while_exists"])
        self.assertIn("text", item)
        self.assertEqual("testing say", item["text"])
        self.assertIn("timestamp", item)
        self.assertIsNotNone(item["timestamp"])
        os.remove(item["file_path"])
        self.assertFalse(os.path.isfile(item["file_path"]))

    def test_say_and_relate_to_file_and_save(self):
        config = AppSettings.create()
        p = PersonalitySettings.create(config.get_personality_path())
        v = VoiceLibrary(config, p)
        v.say("testing say 2", "/home/pi/smartbot/sounds/piano2.m4a", True)
        item = v.get_saying("testing say 2")
        print(item)
        self.assertIn("file_path", item)
        self.assertTrue(os.path.isfile(item["file_path"]))
        self.assertIn("keep_while_exists", item)
        self.assertEqual("/home/pi/smartbot/sounds/piano2.m4a", item["keep_while_exists"])
        self.assertIn("text", item)
        self.assertEqual("testing say 2", item["text"])
        self.assertIn("timestamp", item)
        self.assertIsNotNone(item["timestamp"])
        os.remove(item["file_path"])
        self.assertFalse(os.path.isfile(item["file_path"]))

if __name__ == '__main__':
    unittest.main()
