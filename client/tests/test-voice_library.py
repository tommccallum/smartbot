import unittest
import os
import logging
import sys


sys.path.insert(0, os.path.join(os.path.dirname(__file__),"../src"))

from personality import Personality
from config_io import Configuration
from voice_library import VoiceLibrary


class TestVoiceLibrary(unittest.TestCase):
    def test_say_seconds(self):
        config = Configuration()
        p = Personality(config)
        v = VoiceLibrary(p)
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


if __name__ == '__main__':
    unittest.main()
