import json
import os

from abilities.console_printer import ConsolePrinter
from abilities.mplayer_pause import MplayerPause
from abilities.mplayer_start import MplayerStart
from abilities.text_to_speech import TextToSpeech
from config_io import Configuration
from handler_state import HandlerState


class LiveStreamState(HandlerState):
    @staticmethod
    def create(configuration: Configuration, personality: "Personality", state):
        return LiveStreamState(configuration, personality, state)

    def __init__(self, 
                 configuration: Configuration, 
                 personality: "Personality",
                 state,
                 next_state: HandlerState = None) -> None:
        print("here")
        print(configuration)
        self.configuration = configuration
        self.personality = personality
        self.state_config = state
        self._next_state = next_state
        self.local_conf = os.path.join(self.configuration.config_path, "live_stream.json")
        self.next_track = 0
        self.json=None
        self._read()
        print(configuration)

    def _read(self):
        if os.path.isfile(self.local_conf):
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
        self._context.add(ConsolePrinter("LiveStreamState::on_enter"))
        self.context.add(TextToSpeech("Welcome, you will be now listening to live radio", self.personality))
        track = self.get_next_track()
        self.context.add(TextToSpeech(track["name"], self.personality))
        self.context.add(MplayerStart(track["url"]))
        self.context.execute()

    def on_exit(self):
        self._context.add(ConsolePrinter("LiveStreamState::on_exit"))
        if "mplayer" in self.context.running:
            mplayer = self.context.running["mplayer"]
            mplayer.stop()

    def on_previous_track_down(self):
        next_ability = TextToSpeech("Pausing radio, press the same button to continue", self.personality)
        self.context.add(MplayerPause(on_success=next_ability))

    def on_previous_track_up(self):
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
        self.context.transition_to(self._next_state)
        self.context.execute()

    def on_play_up(self):
        pass

    def on_interrupt(self):
        self.context.running["mplayer"].on_interrupt()

    def on_continue(self):
        self.context.running["mplayer"].on_continue()