import unittest
import os
import unittest
import sys
import time


sys.path.insert(0, os.path.join(os.path.dirname(__file__),"../src"))

CURDIR=os.path.abspath(os.path.dirname(__file__))




from app_context_lock import AppContextLock

class TestAppContextLock(unittest.TestCase):
    def test_lock(self):
        a = AppContextLock()
        self.assertEqual(1, AppContextLock._waiting_process_counter)
        b = AppContextLock()
        self.assertEqual(2, AppContextLock._waiting_process_counter)
        a = None
        self.assertEqual(1, AppContextLock._waiting_process_counter)
        b = None
        self.assertEqual(0, AppContextLock._waiting_process_counter)


if __name__ == '__main__':
    unittest.main()
