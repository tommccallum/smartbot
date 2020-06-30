import os
import unittest
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__),"../src"))

from config_io import Configuration
from personality import Personality

CURDIR=os.path.abspath(os.path.dirname(__file__))

class TestPersonality(unittest.TestCase):
    def test_loading_personality(self):
        config = Configuration(CURDIR+"/test_conf_simple")
        self.assertRaises(FileNotFoundError, Personality, config, "/tmp/__does_not_exist.json" )

    def test_get_voice(self):
        config = Configuration(CURDIR + "/test_conf_simple")
        p = Personality(config, os.path.join(config.get_config_path(), "personality.json"))
        v = p.get_voice()
        self.assertEqual("voice_cmu_us_slt_arctic_clunits", v)
        config._cleanup()

    def test_get_language(self):
        config = Configuration(CURDIR+"/test_conf_simple")
        p = Personality(config, os.path.join(config.get_config_path(),"personality.json"))
        actual = p.get_language()
        self.assertEqual("en", actual)
        config._cleanup()

    def test_get_states(self):
        config = Configuration(CURDIR+"/test_conf_simple")
        p = Personality(config, os.path.join(config.get_config_path(),"personality.json"))
        actual = p.get_states()
        self.assertNotEqual(None, actual)
        config._cleanup()

    def test_has_sleep_mode(self):
        config = Configuration()
        p = Personality(config)
        p.json["sleep"] = {
            "enabled": True,
            "begin": {
                "hard": "09:00",
                "soft": "09:30"
            },
            "end": "17:00",
            "on_end": "Live Radio",
            "phrases": [ "Its only %T, go back to sleep Innogen.",
                "Its not quite morning Innogen, go back to sleep",
                "Its really early Innogen, go back to sleep"
            ]
        }
        self.assertTrue(p.has_sleep_mode())
        self.assertTrue(p.is_sleep_mode_enabled())
        self.assertEqual("09:00",p.get_hard_sleep_time())
        self.assertEqual("09:30", p.get_soft_sleep_time())
        self.assertEqual("17:00", p.get_end_sleep_time())
        self.assertEqual("Live Radio", p.get_on_end_sleep_action())
        self.assertTrue(p.check_sleep_spec_is_valid())

    def test_for_sleep_mode_true(self):
        config = Configuration()
        p = Personality(config)
        p.json["sleep"] = {
            "enabled": True,
            "begin": {
                "hard": "09:00",
                "soft": "09:30"
            },
            "end": "11:40",
            "on_end": "Live Radio",
            "phrases": ["Its only %T, go back to sleep Innogen.",
                        "Its not quite morning Innogen, go back to sleep",
                        "Its really early Innogen, go back to sleep"
                        ]
        }
        self.assertTrue(p.check_for_sleep_mode())

    def test_for_sleep_mode_false(self):
        config = Configuration()
        p = Personality(config)
        p.json["sleep"] = {
            "enabled": True,
            "begin": {
                "hard": "09:00",
                "soft": "09:30"
            },
            "end": "09:40",
            "on_end": "Live Radio",
            "phrases": ["Its only %T, go back to sleep Innogen.",
                        "Its not quite morning Innogen, go back to sleep",
                        "Its really early Innogen, go back to sleep"
                        ]
        }
        self.assertFalse(p.check_for_sleep_mode())


if __name__ == '__main__':
    unittest.main()
