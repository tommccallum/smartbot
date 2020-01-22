import json
import os

from abilities.console_printer import ConsolePrinter
from abilities.mplayer_start import MplayerStart
from abilities.text_to_speech import TextToSpeech
from config_io import Configuration
from handler_state import HandlerState


class LiveStreamState(HandlerState):
    @staticmethod
    def create(configuration: Configuration, personality: "Personality"):
        return LiveStreamState(configuration, personality)

    def __init__(self, configuration: Configuration, personality: "Personality",
                 next_state: HandlerState = None) -> None:
        self.configuration = configuration
        self.personality = personality
        self._next_state = next_state
        self.local_conf = os.path.join(self.configuration.config_path, "live_stream.json")
        self.next_track = 0
        self.json=None
        self._read()

    def _read(self):
        with open(self.local_conf, "r") as conf:
            self.json = json.load(conf)

    def get_track_count(self):
        if not "playlist" in self.json:
            return 0
        return len(self.json["playlist"])

    def get_next_track(self):
        track = None
        if "playlist" in self.json:
            n = self.get_track_count()
            if self.next_track >= n:
                self.context.add(TextToSpeech("Moving to start of the list of stations", self.personality))
                self.next_track = 0
            if n > 0 and self.next_track < n:
                track = self.json["playlist"][self.next_track]
                self.next_track += 1
        return track

    def set_next_state(self, next):
        self._next_state = next

    def on_enter(self):
        self._context.add(ConsolePrinter("RadioState::on_enter"))
        track = self.get_next_track()
        self.context.add(TextToSpeech(track["name"], self.personality))
        self.context.add(MplayerStart(track["url"]))
        self.context.execute()

    def on_exit(self):
        self._context.add(ConsolePrinter("RadioState::on_exit"))
        if "mplayer" in self.context.running:
            mplayer = self.context.running["mplayer"]
            mplayer.stop()

    def on_previous_track_down(self):
        self.context.add(TextToSpeech("Pausing radio", self.personality))

    def on_previous_track_up(self):
        # self.context.add(mplayer_pause())
        self.context.execute()

    def on_next_track_down(self):
        if "mplayer" in self.context.running:
            mplayer = self.context.running["mplayer"]
            mplayer.stop()
        track = self.get_next_track()
        self.context.add(TextToSpeech("Next show is "+track["name"], self.personality))
        self.context.add(MplayerStart(track["url"]))

    def on_next_track_up(self):
        self.context.execute()

    def on_play_down(self):
        self.context.add(TextToSpeech("Pausing radio", self.personality))
        self.context.transition_to(self._next_state)
        self.context.execute()

    def on_play_up(self):
        pass
