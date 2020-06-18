import logging
import unittest
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__),"../src"))

from keyboard_thread import KeyboardListener
import time


class TestKeyboardThread(unittest.TestCase):

    def test_keys(self):
        root = logging.getLogger()
        root.setLevel(logging.DEBUG)
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter('[%(asctime)s] [%(module)s::%(funcName)s] [%(levelname)s] %(message)s',
                                      datefmt="%Y-%m-%d %H:%M:%S")
        handler.setFormatter(formatter)
        root.addHandler(handler)

        k = KeyboardListener()
        k.start()
        time.sleep(3)


if __name__ == '__main__':
    unittest.main()
