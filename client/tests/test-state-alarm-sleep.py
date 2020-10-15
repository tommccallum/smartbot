import unittest
import datetime
import os
import unittest
import time
import logging
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__),"../src"))


class TestAlarmSleepTransition(unittest.TestCase):
    def test_when_sleeping_and_alarm_goes_off(self):
        self.assertEqual(True, False)


if __name__ == '__main__':
    unittest.main()
