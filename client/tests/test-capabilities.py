import unittest
import os
import sys
import logging

sys.path.insert(0, os.path.join(os.path.dirname(__file__),"../src"))

from capabilities import Capabilities
import globalvars

class TestCapabilities(unittest.TestCase):

    def test_creation(self):
        capabilities = Capabilities()
        self.assertTrue(capabilities.expect_bluetooth_speaker())
        self.assertTrue(capabilities.expect_identity())
        self.assertTrue(capabilities.expect_internet())
        self.assertTrue(capabilities.expect_keyboard())
        self.assertTrue(capabilities.expect_network())

    def test_printout(self):
        capabilities = Capabilities()
        actual = str(capabilities)
        self.assertEqual("Identity=True, Bt Speaker=True, Lnet=True, Inet=True, Keyb=True", actual)

    def test_identity_arg(self):
        args = [ "-owners" ]
        capabilities = Capabilities(args)
        self.assertFalse(capabilities.expect_identity())

    def test_bt_speaker_arg(self):
        args = [ "-bluetooth-speaker" ]
        capabilities = Capabilities(args)
        self.assertFalse(capabilities.expect_bluetooth_speaker())

    def test_keyboard_arg(self):
        args = ["-keyboard"]
        capabilities = Capabilities(args)
        self.assertFalse(capabilities.expect_keyboard())

    def test_inet_arg(self):
        args = ["-internet-monitor"]
        capabilities = Capabilities(args)
        self.assertFalse(capabilities.expect_internet())

    def test_lnet_arg(self):
        args = ["-network-monitor"]
        capabilities = Capabilities(args)
        self.assertFalse(capabilities.expect_network())


if __name__ == '__main__':
    unittest.main()
