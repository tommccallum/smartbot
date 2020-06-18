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


if __name__ == '__main__':
    unittest.main()
