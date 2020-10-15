import unittest
import os
import unittest
import sys
import time
sys.path.insert(0, os.path.join(os.path.dirname(__file__),"../src"))

CURDIR=os.path.abspath(os.path.dirname(__file__))

from skills.timer import Timer


class TestTimer(unittest.TestCase):
    def test_start(self):
        t = Timer(3)
        self.assertEqual(3, t.elapsedTime())

    def test_start(self):
        t = Timer(3)
        self.assertEqual(3, t.elapsedTime())

    def test_stop(self):
        t = Timer()
        time.sleep(2)
        t.stop()
        self.assertEqual(2, t.elapsedTime())

    def test_resume(self):
        t = Timer()
        time.sleep(2)
        t.stop()
        time.sleep(2)
        t.resume()
        time.sleep(2)
        self.assertEqual(4, t.elapsedTime())
        time.sleep(2)
        t.stop()
        self.assertEqual(6, t.elapsedTime())


if __name__ == '__main__':
    unittest.main()
