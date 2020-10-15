import os
import sys
import unittest


sys.path.insert(0, os.path.join(os.path.dirname(__file__),"../src"))


class TestAppState(unittest.TestCase):

    def test_load_from_dict(self):
        self.assertEqual(True, False)

    def test_load_from_non_default_location(self):
        self.assertEqual(True, False)

    def test_load_from_default_location(self):
        self.assertEqual(True, False)

    def test_reload_from_dict(self):
        self.assertEqual(True, False)


if __name__ == '__main__':
    unittest.main()
