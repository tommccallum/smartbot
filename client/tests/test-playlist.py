import glob
import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__),"../src"))

from playlist import Playlist


class TestPlaylist(unittest.TestCase):

    def test_empty_playlist(self):
        self.assertRaises(ValueError, Playlist, None)

    def test_empty_playlist2(self):
        p = Playlist([])
        self.assertEqual(p.size(), 0)

    def test_error(self):
        self.assertRaises(ValueError, Playlist, {})

    def test_stream(self):
        trackList = [
            {"name": "BBC Radio 2", "url": "http://bbcmedia.ic.llnwd.net/stream/bbcmedia_radio2_mf_p"}
        ]
        p = Playlist(trackList)
        self.assertEqual(p.size(), 1)

        item = p.first()
        self.assertEqual(item, trackList[0])
        item = p.last()
        self.assertEqual(item, trackList[0])
        for ii in range(0,5):
            item = p.next()
            self.assertEqual(item, trackList[0])
        for ii in range(5,-5):
            item = p.prev()
            self.assertEqual(item, trackList[0])
        p.shuffle()
        item = p.first()
        self.assertEqual(item, trackList[0])
        item = p.last()
        self.assertEqual(item, trackList[0])
        for ii in range(0, 5):
            item = p.next()
            self.assertEqual(item, trackList[0])
        for ii in range(5, -5):
            item = p.prev()
            self.assertEqual(item, trackList[0])

    def test_stream_2(self):
        trackList = [
            {"name": "BBC Radio 2", "url": "http://bbcmedia.ic.llnwd.net/stream/bbcmedia_radio2_mf_p"},
            {"name": "BBC Radio 4", "url": "http://bbcmedia.ic.llnwd.net/stream/bbcmedia_radio4_mf_p"}
        ]
        p = Playlist(trackList)
        self.assertEqual(p.size(), 2)

        item = p.first()
        self.assertEqual(item, trackList[0])
        item = p.last()
        self.assertEqual(item, trackList[1])
        for ii in range(0,5):
            item = p.next()
            self.assertEqual(item, trackList[ii%2])
        for ii in range(5,-5):
            item = p.prev()
            self.assertEqual(item, trackList[ii%2])

    def test_directory(self):
        trackList = [
            "/home/pi/smartbot/media/recent"
        ]
        p = Playlist(trackList)
        self.assertEqual(p.size(), 4)

    def test_directory_repeat(self):
        trackList = [
            "/home/pi/smartbot/media/recent",
            "/home/pi/smartbot/media/recent"
        ]
        p = Playlist(trackList)
        self.assertEqual(p.size(), 4)

    def test_directory_none(self):
        trackList = [
            "/home/pi/smartbot/media/radio"
        ]
        p = Playlist(trackList)
        files = glob.glob("/home/pi/smartbot/media/radio/*")
        self.assertEqual(p.size(), len(files))

    def test_directory_not_recursive(self):
        trackList = [
            { "directory":"/home/pi/smartbot/media", "include-subdir":False }
        ]
        p = Playlist(trackList)
        self.assertEqual(p.size(), 0)

    def test_directory_extensions_1(self):
        trackList = [
            { "directory":"/home/pi/smartbot/media/recent", "include-subdir":True, "extensions": None }
        ]
        p = Playlist(trackList)
        self.assertEqual(p.size(), 4)

    def test_directory_extensions_2(self):
        trackList = [
            { "directory":"/home/pi/smartbot/media/recent", "include-subdir":True, "extensions": [] }
        ]
        p = Playlist(trackList)
        self.assertEqual(p.size(), 4)

    def test_directory_extensions_3(self):
        trackList = [
            { "directory":"/home/pi/smartbot/media/recent", "include-subdir":True, "extensions": ["m4a"] }
        ]
        p = Playlist(trackList)
        self.assertEqual(p.size(), 4)

    def test_directory_extensions_4(self):
        trackList = [
            { "directory":"/home/pi/smartbot/media/recent", "include-subdir":True, "extensions": "m4a" }
        ]
        p = Playlist(trackList)
        self.assertEqual(p.size(), 4)

    def test_ordering_invalid_field(self):
        trackList = [
            {"name": "a", "date": 0, "url": "/home/pi/smartbot/sounds/Marconi_Union-Weightless.mp3"},
            {"name": "c", "date": 2, "url": "/home/pi/smartbot/sounds/can_you_hear_me.wav"},
            {"name": "b", "date": 1, "url": "/home/pi/smartbot/sounds/Tardis-sound.wav"},
        ]
        p = Playlist(trackList)
        p.sort("somethingwrong")
        # should sort by name
        self.assertListEqual(p.ordering, [0,2,1])

    def test_ordering_name_asc(self):
        trackList = [
            {"name": "a", "date": 0, "url": "/home/pi/smartbot/sounds/Marconi_Union-Weightless.mp3"},
            {"name": "c", "date": 2, "url": "/home/pi/smartbot/sounds/can_you_hear_me.wav"},
            {"name": "b", "date": 1, "url": "/home/pi/smartbot/sounds/Tardis-sound.wav"},
        ]
        p = Playlist(trackList)
        p.sort("name")
        self.assertListEqual(p.ordering, [0, 2, 1])

    def test_ordering_name_desc(self):
        trackList = [
            {"name": "a", "date": 0, "url": "/home/pi/smartbot/sounds/Marconi_Union-Weightless.mp3"},
            {"name": "c", "date": 2, "url": "/home/pi/smartbot/sounds/can_you_hear_me.wav"},
            {"name": "b", "date": 1, "url": "/home/pi/smartbot/sounds/Tardis-sound.wav"},
        ]
        p = Playlist(trackList)
        p.sort(["name","descending"])
        self.assertListEqual(p.ordering, [1, 2, 0])

    def test_ordering_date_asc(self):
        trackList = [
            {"name": "a", "date": 0, "url": "/home/pi/smartbot/sounds/Marconi_Union-Weightless.mp3"},
            {"name": "c", "date": 2, "url": "/home/pi/smartbot/sounds/can_you_hear_me.wav"},
            {"name": "b", "date": 1, "url": "/home/pi/smartbot/sounds/Tardis-sound.wav"},
        ]
        p = Playlist(trackList)
        p.sort("date")
        self.assertListEqual(p.ordering, [0, 2, 1])

    def test_ordering_date_asc_2(self):
        trackList = [
            {"name": "a", "date": 0, "url": "/home/pi/smartbot/sounds/Marconi_Union-Weightless.mp3"},
            {"name": "c", "date": 2, "url": "/home/pi/smartbot/sounds/can_you_hear_me.wav"},
            {"name": "b", "date": 1, "url": "/home/pi/smartbot/sounds/Tardis-sound.wav"},
        ]
        p = Playlist(trackList)
        p.sort(["date","ascending"])
        self.assertListEqual(p.ordering, [0, 2, 1])

    def test_ordering_date_desc(self):
        trackList = [
            {"name": "a", "date": 0, "url": "/home/pi/smartbot/sounds/Marconi_Union-Weightless.mp3"},
            {"name": "c", "date": 2, "url": "/home/pi/smartbot/sounds/can_you_hear_me.wav"},
            {"name": "b", "date": 1, "url": "/home/pi/smartbot/sounds/Tardis-sound.wav"},
        ]
        p = Playlist(trackList)
        p.sort(["date","descending"])
        self.assertListEqual(p.ordering, [1, 2, 0])


if __name__ == '__main__':
    unittest.main()
