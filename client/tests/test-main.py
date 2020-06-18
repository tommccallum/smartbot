import unittest
import os
import unittest
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__),"../src"))

CURDIR=os.path.abspath(os.path.dirname(__file__))

from main import app_init, start_event_device_agent


class TestMain(unittest.TestCase):
    def test_something(self):
        config, context = app_init(CURDIR+"/test_conf_simple")

    def test_main_loop(self):
        config, context = app_init(CURDIR+"/test_conf_simple")
        self.assertRaises(ValueError, start_event_device_agent, config,context)


if __name__ == '__main__':
    unittest.main()
