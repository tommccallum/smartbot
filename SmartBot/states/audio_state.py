import glob
import json
import os
import re
import string

from abilities.console_printer import ConsolePrinter
from abilities.mplayer_pause import MplayerPause
from abilities.mplayer_start import MplayerStart
from abilities.text_to_speech import TextToSpeech
from config_io import Configuration, HOME_DIRECTORY
from handler_state import HandlerState


class AudioState(HandlerState):
    @staticmethod
    def create(configuration: Configuration, personality: "Personality", state):
        return AudioState(configuration, personality, state)

    def __init__(self,
                 configuration: Configuration,
                 personality: "Personality",
                 state,
                 next_state: HandlerState = None) -> None:
        self.configuration = configuration
        self.personality = personality
        self.config = state
        self._next_state = next_state
        self.local_conf = os.path.join(self.configuration.config_path, "audio.json")
        self.next_track = 0
        self.json=None
        self._read()


    def _read(self):
        if os.path.isfile(self.local_conf):
            with open(self.local_conf, "r") as conf:
                self.json = json.load(conf)

    def _build_playlist(self):
        if not self.config:
            return

        recursive = False
        local_path = None
        files = []
        if "path" in self.config:
            local_path = self.config["path"]
            local_path = local_path.replace("%HOME%", HOME_DIRECTORY)
            local_path = local_path.replace("%CONFIG%", self.configuration.config_path)
        if not local_path:
            raise ValueError("Invalid audio directory specified")
        self._context.add(ConsolePrinter("AudioState::path="+local_path))

        if "recursive" in self.config:
            recursive = self.config["recursive"] == "true"

        if "extensions" in self.config:
            exts = self.config["extensions"].split(",")
        else:
            exts = [ "m4a" ]

        if len(exts) > 0:
            for ext in exts:
                if len(ext) > 0 and ext.isalnum():
                    if local_path:
                        if self.config["extensions"]:
                            files = glob.glob(os.path.join(local_path,"/*."+ext), recursive=recursive)

        # pattern to match non characters
        pattern = re.compile('[\W]+')
        for file in files:
            track_name = os.path.basename(file)
            track_name = track_name[:track_name.rfind('.')]
            track_name = pattern.sub(" ", track_name)
            track_date = os.path.getmtime(file)
            track = {
                "name": track_name,
                "url": file
            }
            self.tracks.append(track)

        ordering = "name"
        ascending = True
        if "orderby" in self.config:
            ordering = self.config["orderby"]
            descending = False
            if ordering is list:
                if len(ordering) > 1:
                    descending = ordering[1].upper() == "DESC"
                    ordering = ordering[0]
                else:
                    ordering = ordering[0]
        self.tracks = sorted(self.tracks, key=lambda k: k[ordering], reverse=descending)

        for t in self.tracks:
            self._context.add(ConsolePrinter("AudioState::add{" + track_name + "," + file + "}"))

    def get_track_count(self):
        return len(self.tracks)

    def get_next_track(self):
        track = None
        n = self.get_track_count()
        if self.next_track >= n:
            self.context.add(TextToSpeech("Moving to start of the list of programmes", self.personality))
            self.next_track = 0
        if n > 0 and self.next_track < n:
            track = self.tracks[self.next_track]
            self.next_track += 1
        return track

    def set_next_state(self, next):
        self._next_state = next

    def on_enter(self):
        self._context.add(ConsolePrinter("AudioState("+self.config.name+")::on_enter"))
        self.context.add(TextToSpeech("Welcome to "+self.config.title, self.personality))
        self._build_playlist() # refresh list
        track = self.get_next_track()
        self.context.add(TextToSpeech(track["name"], self.personality))
        self.context.add(MplayerStart(track["url"]))
        self.context.execute()

    def on_exit(self):
        self._context.add(ConsolePrinter("AudioState("+self.config.name+")::on_exit"))
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
        self.context.add(TextToSpeech("Next track is "+track["name"], self.personality))
        self.context.add(MplayerStart(track["url"]))

    def on_next_track_up(self):
        self.context.execute()

    def on_play_down(self):
        self.context.transition_to(self._next_state)
        self.context.execute()

    def on_play_up(self):
        pass
