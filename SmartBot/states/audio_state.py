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
        self.state_config = state
        self._next_state = next_state
        self.local_conf = os.path.join(self.configuration.config_path, "audio.json")
        self.next_track = 0
        self.json=None
        self.tracks = []
        self._read()


    def _read(self):
        if os.path.isfile(self.local_conf):
            with open(self.local_conf, "r") as conf:
                self.json = json.load(conf)

    def _build_playlist(self):
        print(self.state_config)
        if not self.state_config:
            return

        recursive = False
        local_path = None
        files = []
        self.tracks = []
        if "path" in self.state_config:
            local_path = self.state_config["path"]
            local_path = local_path.replace("%HOME%", HOME_DIRECTORY)
            local_path = local_path.replace("%CONFIG%", self.configuration.config_path)
        if not local_path:
            raise ValueError("Invalid audio directory specified")
        self._context.add(ConsolePrinter("AudioState::path="+local_path))

        if "recursive" in self.state_config:
            recursive = self.state_config["recursive"] == "true"

        if "extensions" in self.state_config:
            exts = self.state_config["extensions"].split(",")
        else:
            exts = [ "m4a" ]

        print(local_path)
        print(exts)

        if len(exts) > 0:
            for ext in exts:
                if len(ext) > 0 and ext.isalnum():
                    if local_path:
                        files = glob.glob(os.path.join(local_path,"*."+ext), recursive=recursive)

        print(files)

        # pattern to match non characters
        pattern = re.compile('[\W_]+')
        has_num = re.compile('[0-9]+')
        has_ch = re.compile('[a-zA-Z]+')
        for file in files:
            track_name = os.path.basename(file)
            track_name = track_name[:track_name.rfind('.')]
            track_name = pattern.sub(" ", track_name)
            words = track_name.split(" ")
            print(words)
            # remove words that are sequences of multiple letters and numbers
            # e.g.  M9 is OK
            #       BBC2 is OK
            #       m4823702aqs is not
            #       md23212 is not
            #       m23213 is not
            words = [ w for w in words if not has_num.search(w) and has_ch.search(w) ]
            print(words)
            track_name = " ".join(words)
            track_date = os.path.getmtime(file)
            track = {
                "name": track_name,
                "url": file
            }
            self.tracks.append(track)

        ordering = "name"
        ascending = True
        if "orderby" in self.state_config:
            ordering = self.state_config["orderby"]
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
        self._context.add(ConsolePrinter("AudioState("+self.state_config["name"]+")::on_enter"))
        self.context.add(TextToSpeech("Welcome to "+self.state_config["title"], self.personality))
        self._build_playlist() # refresh list
        track = self.get_next_track()
        if track:
            self.context.add(TextToSpeech(track["name"], self.personality))
            self.context.add(MplayerStart(track["url"]))
            self.context.execute()
        else:
            self.on_empty_playlist()

    def on_empty_playlist(self):
        self.context.add(TextToSpeech("There are no tracks available.", self.personality))
        self._context.add(ConsolePrinter("AudioState("+self.state_config["name"]+")::on_empty_playlist"))

    def on_exit(self):
        self._context.add(ConsolePrinter("AudioState("+self.state_config["name"]+")::on_exit"))
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
        if track:
            self.context.add(TextToSpeech("Next track is "+track["name"], self.personality))
            self.context.add(MplayerStart(track["url"]))
        else:
            self.on_empty_playlist()

    def on_next_track_up(self):
        self.context.execute()

    def on_play_down(self):
        self.context.transition_to(self._next_state)
        self.context.execute()

    def on_play_up(self):
        pass
