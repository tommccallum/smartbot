import unittest
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__),"../src"))


from app_settings import AppSettings, create_app_settings

CURDIR=os.path.abspath(os.path.dirname(__file__))

class TestAppSettings(unittest.TestCase):

    def test_home_directory(self):
        self.assertEqual("/home/pi", AppSettings.HOME_DIRECTORY)

    def test_smartbot_home(self):
        self.assertEqual("/home/pi/smartbot", AppSettings.SMARTBOT_HOME)

    def test_creation(self):
        file_path = CURDIR+"/test_conf_simple/config.json"
        # create
        conf = create_app_settings(file_path)
        self.assertEqual("/home/pi/.config/smartbot/fifos", conf.get_fifo_path())
        self.assertEqual("/home/pi/.config/smartbot/personality.json", conf.get_personality_path())
        self.assertEqual("/home/pi/.config/smartbot/devices.json", conf.get_devices_path())
        self.assertEqual("/home/pi/.config/smartbot", conf.get_config_path())
        # release
        conf = None

    # def test_loading_nonexistent_file(self):
    #     self.assertRaises(FileNotFoundError, Configuration, "/tmp/__definitely_does_not_exist.json" )
    #
    # def test_loading_default_config(self):
    #     config = Configuration(CURDIR+"/test_conf_simple/config.json")
    #     self.assertNotEqual( config.json, None)
    #     self.assertEqual(type(config.json), dict)
    #     config._cleanup()
    #
    # def test_paths(self):
    #     config = Configuration(CURDIR+"/test_conf_simple")
    #     self.assertEqual(os.path.abspath(CURDIR+"/test_conf_simple/fifos"),config.get_fifo_directory())
    #     config._cleanup()

    def tearDown(self):
        pass

if __name__ == '__main__':
    unittest.main()
