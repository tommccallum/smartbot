import unittest
import os
import unittest
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__),"../src"))

CURDIR=os.path.abspath(os.path.dirname(__file__))

from main import init_application


class TestMain(unittest.TestCase):
    def test_init_application(self):
        init_application(CURDIR+"/test_conf_simple")


if __name__ == '__main__':
    unittest.main()
