import unittest

from main import app_init, app_main_loop


class TestMain(unittest.TestCase):
    def test_something(self):
        config, context = app_init()

    def test_main_loop(self):
        config, context = app_init()
        self.assertRaises(ValueError, app_main_loop, config,context)


if __name__ == '__main__':
    unittest.main()
