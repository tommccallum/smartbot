import os
import unittest
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__),"../src"))

from personality_settings import PersonalitySettings, create_personality_settings


class TestPersonalitySettings(unittest.TestCase):
    def test_get_voice(self):
        p = create_personality_settings(os.path.join(os.path.dirname(__file__),"test_conf_simple","personality.json"))
        v = p.get_voice()
        self.assertEqual("voice_cmu_us_slt_arctic_clunits", v)

    def test_get_language(self):
        p = create_personality_settings(os.path.join(os.path.dirname(__file__),"test_conf_simple","personality.json"))
        actual = p.get_language()
        self.assertEqual("en", actual)

    # def test_get_states(self):
    #     config = AppSettings(CURDIR+"/test_conf_simple")
    #     p = PersonalitySettings(config, os.path.join(config.get_config_path(),"personality.json"))
    #     actual = p.get_states()
    #     self.assertNotEqual(None, actual)
    #     config._cleanup()

    def test_has_sleep_mode(self):
        p = create_personality_settings(os.path.join(os.path.dirname(__file__),"test_conf_simple","personality.json"))
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
        self.assertIsNotNone(p.get_sleep_mode())


if __name__ == '__main__':
    unittest.main()
