import unittest

from config_io import Configuration


class TestConfiguration(unittest.TestCase):
    def test_loading_nonexistent_file(self):
        self.assertRaises(FileNotFoundError, Configuration, "/tmp/__definitely_does_not_exist.json" )

    def test_loading_default_config(self):
        config = Configuration("../conf/config.json")
        self.assertNotEqual( config.json, None)
        self.assertEqual(type(config.json), dict)

    def test_loading_default_config_from_user_home(self):
        config = Configuration()
        self.assertNotEqual( config.json, None)
        self.assertEqual(type(config.json), dict)


if __name__ == '__main__':
    unittest.main()
