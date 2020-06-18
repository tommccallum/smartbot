import unittest
import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__),"../src"))



from keyboard_thread import KeyboardListener


from config_io import Configuration
from skills.mplayer import MPlayer

CURDIR=os.path.abspath(os.path.dirname(__file__))

class TestMPlayer(unittest.TestCase):
    def setUp(self):
        DEFAULT_CONFIG_LOCATION=CURDIR+"/test_conf_simple"

    def test_single_instance(self):
        config = Configuration(CURDIR + "/test_conf_simple")
        MPlayer.instance_counter = 1
        mplayer = MPlayer(config)
        self.assertEqual(mplayer.instance_id, 1)

    def test_multiple_instances(self):
        config = Configuration(CURDIR + "/test_conf_simple")
        mplayer2 = MPlayer(config)
        mplayer1 = MPlayer(config)
        self.assertNotEqual(mplayer1.instance_id, mplayer2.instance_id)

    def test_shutdown(self):
        config = Configuration(CURDIR + "/test_conf_simple")
        mplayer = MPlayer(config)
        mplayer.start(CURDIR + "/../../sounds/piano2.m4a")
        time.sleep(3)
        mplayer.stop()

    def test_shutdown(self):
        keyboard_thread = KeyboardListener()
        keyboard_thread.add_listener(self)
        keyboard_thread.start()
        config = Configuration(CURDIR + "/test_conf_simple")
        mplayer = MPlayer(config)
        mplayer.start("http://bbcmedia.ic.llnwd.net/stream/bbcmedia_radio2_mf_p")
        for ii in range(0,5):
            print("Attempt {}".format(ii))
            time.sleep(3)
            mplayer.pause()
            time.sleep(3)
            mplayer.play()
        time.sleep(3)
        mplayer.stop()
        keyboard_thread.stop()

if __name__ == '__main__':
    unittest.main()
