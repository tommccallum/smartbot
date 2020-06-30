import logging
import unittest
import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__),"../src"))

from globalvars import setup_logging
from keyboard_thread import KeyboardListener


class TestKeyboardThread(unittest.TestCase):

    def test_keys(self):
        """
        Test is the keyboard picks up on arrow keys, requires user input
        :return:
        """
        setup_logging()

        k = KeyboardListener()
        k.start()
        time.sleep(3)
        k.stop()

if __name__ == '__main__':
    unittest.main()
