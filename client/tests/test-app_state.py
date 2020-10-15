import unittest
import unittest
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../src"))
CURDIR = os.path.abspath(os.path.dirname(__file__))
from app_state import AppState
from local_logging import setup_logging


class TestAppState(unittest.TestCase):
    def test_create_from_dict(self):
        values = {
            "config": {
                "owner": "Innogen",
                "personality": "personality.json",
                "devices": {
                    "path": "devices.json"
                },
                "output": {
                    "sink": "org.bluez",
                    "device": "D0:8A:55:00:9C:27"
                },
                "alarms": []
            }
        }
        state = AppState.create_from_dict(values)
        self.assertEqual(dict, type(state.dev_specified_configuration))

    def test_create_from_dict(self):
        values = {
            "config": {
                "owner": "Innogen",
                "personality": "personality.json",
                "devices": {
                    "path": "devices.json"
                },
                "output": {
                    "sink": "org.bluez",
                    "device": "D0:8A:55:00:9C:27"
                },
                "alarms": []
            },
            "personality": {
                "name": "April",
                "conf": {
                    "festival": {
                        "voice": "voice_kal_diphone"
                    },
                    "language": "en"
                },
                "sleep": {
                    "enabled": True,
                    "begin": {
                        "hard": "09:00",
                        "soft": "09:30"
                    },
                    "end": "20:25",
                    "on_enter": "%SMARTBOT%/sounds/Marconi_Union-Weightless-sleepversion.mp3",
                    "on_end": "Silence",
                    "phrases": ["Its only %T, go back to sleep Innogen.",
                                "Its not quite morning Innogen, go back to sleep",
                                "Its really early Innogen, go back to sleep"
                                ]
                },
                "states": [{
                    "type": "introduction",
                    "filename": "introduction.json"
                }, {
                    "type": "audio",
                    "title": "Live Radio",
                    "filename": "live_stream.json",
                    "on_enter": "You are now listening to live radio.",
                    "on_empty": "There are no radio stations available."
                }, {
                    "type": "audio",
                    "title": "Saved Programmes",
                    "filename": "saved_programmes.json",
                    "playlist": {
                        "tracks": [
                            {"directory": "%SMARTBOT%/media/radio", "extensions": "m4a", "include-subdir": True}
                        ],
                        "orderby": "name"
                    },
                    "on_enter": "You are now listening to your favourites.",
                    "on_empty": "There are no favourites chosen yet."
                },
                    {
                        "type": "audio",
                        "title": "Latest Programmes",
                        "filename": "latest_programmes.json",
                        "playlist": {
                            "tracks": [
                                {"directory": "%SMARTBOT%/media/recent", "extensions": "m4a", "include-subdir": True}
                            ],
                            "orderby": ["date", "desc"]
                        },
                        "on_enter": "You are now listening to the latest programmes.",
                        "on_empty": "There are no programmes downloaded yet."
                    },
                    {
                        "type": "audio",
                        "title": "Lets Dance",
                        "filename": "lets_dance.json",
                        "playlist": {
                            "tracks": [
                                {"directory": "%SMARTBOT%/media/lets_dance", "extensions": "m4a",
                                 "include-subdir": True}
                            ],
                            "orderby": ["name", "asc"]
                        },
                        "on_enter": "Let's Dance!",
                        "on_empty": "There are no songs available yet."
                    },
                    {
                        "type": "speakingclock",
                        "title": "Speaking Clock",
                        "on_enter": False
                    },
                    {
                        "type": "facts",
                        "title": "Funky Facts",
                        "filename": "facts_*.json",
                        "on_enter": {
                            "type": "sound",
                            "path": "%SMARTBOT%/sounds/gojetters-funkyfacts.wav"
                        },
                        "on_empty": "There are no funky facts available."
                    }
                ]},
            "Lets Dance": {
                "tracks": {

                }
            }
        }
        setup_logging()
        state = AppState.create_from_dict(values)
        self.assertEqual(dict, type(state.dev_specified_configuration))

    def test_create_from_file(self):
        app_state = AppState.create_from_file(os.path.join(CURDIR,"test_conf_simple","config.json"))
        self.assertEqual(str(app_state.context.__class__), "<class 'user_context.UserContext'>")

if __name__ == '__main__':
    unittest.main()
