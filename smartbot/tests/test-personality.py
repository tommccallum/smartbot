import os
import unittest

from config_io import Configuration
from personality_io import Personality


class TestPersonality(unittest.TestCase):
    def test_loading_personality(self):
        config = Configuration("../conf/config.json")
        self.assertRaises(FileNotFoundError, Personality, config, "/tmp/__does_not_exist.json" )

    def test_get_voice(self):
        config = Configuration("../conf/config.json")
        p = Personality(config, os.path.abspath("../conf/personality.json"))
        v = p.get_voice()
        self.assertEqual("voice_cmu_us_slt_arctic_clunits", v)

    def test_get_language(self):
        config = Configuration("../conf/config.json")
        p = Personality(config, os.path.abspath("../conf/personality.json"))
        actual = p.get_language()
        self.assertEqual("en", actual)

    def test_get_states(self):
        config = Configuration("../conf/config.json")
        p = Personality(config, os.path.abspath("../conf/personality.json"))
        actual = p.get_states()
        self.assertNotEqual(None, actual)

if __name__ == '__main__':
    unittest.main()
