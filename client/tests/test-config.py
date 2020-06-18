import unittest
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__),"../src"))


from config_io import Configuration

CURDIR=os.path.abspath(os.path.dirname(__file__))

class TestConfiguration(unittest.TestCase):
    def test_loading_nonexistent_file(self):
        self.assertRaises(FileNotFoundError, Configuration, "/tmp/__definitely_does_not_exist.json" )

    def test_loading_default_config(self):
        config = Configuration(CURDIR+"/test_conf_simple/config.json")
        self.assertNotEqual( config.json, None)
        self.assertEqual(type(config.json), dict)
        config._cleanup()

    def test_paths(self):
        config = Configuration(CURDIR+"/test_conf_simple")
        self.assertEqual(os.path.abspath(CURDIR+"/test_conf_simple/fifos"),config.get_fifo_directory())
        config._cleanup()

    def tearDown(self):
        pass

if __name__ == '__main__':
    unittest.main()
