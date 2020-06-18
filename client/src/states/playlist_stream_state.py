import json
import os
import logging
import time

from config_io import Configuration
from event import Event, EventEnum
from playlist import Playlist
from skills.mplayer import MPlayer
from states.state import State


class PlaylistStreamState(State):
    """
        Plays a set of live streams
    """
    @staticmethod
    def create(configuration: Configuration, personality: "Personality", state_configuration):
        return PlaylistStreamState(configuration, personality, state_configuration)

    def __init__(self,
                 configuration: Configuration,
                 personality: "Personality",
                 state_configuration
                 ) -> None:
        super(PlaylistStreamState, self).__init__(configuration, personality, state_configuration)
        self.next_track = 0
        self.current_track = None
        self.playlist = None
        self.playlist_config = None
        self.last_checkpoint = None

        print("Creating a PlaylistStreamState")
        self.mplayer = MPlayer(configuration)

        playlist = self.json
        if "playlist" in self.state_config:
            logging.debug("loading playlist from personality spec")
            playlist = self.state_config["playlist"]
        logging.debug(playlist)
        self.load_playlist(playlist)

    def load_playlist(self, playlist_config):
        """
        loading the playlist, allows us to override configuration playlist easily
        {
        "playlist": [],
        "shuffle": bool,
        "orderby": [ field, desc/_asc_ ]
        }
        """
        self.playlist_config = playlist_config
        logging.debug(playlist_config)
        self.playlist = Playlist([])
        if playlist_config:
            if not "tracks" in playlist_config:
                logging.error("no tracks key specified in playlist")
                logging.error(playlist_config)
                raise ValueError("no tracks key specified in playlist")
            self.playlist = Playlist(playlist_config["tracks"], self.configuration.HOME_DIRECTORY, self.configuration.get_config_path())
            if "shuffle" in playlist_config:
                if playlist_config["shuffle"]:
                    self.playlist.shuffle()
            if "orderby" in playlist_config:
                self.playlist.sort(playlist_config["orderby"])
        logging.debug(self.playlist)

    def _save_state(self, values):
        """
        Save where the user got to on this
        :param values:
        :return:
        """
        values["user_state"] = {}
        if self.current_track and self.mplayer:
            values["user_state"]["track"] = self.current_track
            values["user_state"]["seek"] = self.mplayer.get_play_duration()
        logging.debug("saving state as {}".format(values["user_state"]))
        return values

    def get_track_count(self):
        return self.playlist.size()

    def get_next_track(self):
        self.current_track =  self.playlist.next()
        if self.current_track is None:
            return self.current_track
        if not "name" in self.current_track:
            # sometimes name will be missing for instance if our tracks came from a directory automatically
            # in which case we convert the filename to something we can say
            self.current_track["name"] = self.personality.voice_library.convert_filename_to_speech_text(self.current_track["url"])
        return self.current_track

    def on_empty_playlist(self):
        if "on_empty" in self.state_config:
            self.personality.voice_library.say(self.state_config["on_empty"])
        else:
            self.personality.voice_library.say("There are no tracks available on this playlist.")

    def on_enter(self):
        logging.debug("LiveStreamState::on_enter")
        if "on_enter" in self.state_config:
            self.personality.voice_library.say(self.state_config["on_enter"])
        else:
            self.personality.voice_library.say("Welcome, you will be now listening to live radio")

        # load an existing state if one exists
        seek = 0
        track = None
        if not self.mplayer.is_paused():
            # if the mplayer is not paused then this must be a new session
            # so we want to load where we were last time for this mode
            # if we have a saved session that is
            user_state = self._get_user_state()
            if user_state is not None:
                if "seek" in user_state:
                    seek = user_state["seek"]
                if "track" in user_state:
                    track = user_state["track"]
                    self.current_track = track
                    self.playlist.set_current(track)
        self._play_next_track(track, seek)

    def on_exit(self):
        logging.debug("state exiting")
        if not self.mplayer.is_paused():
            logging.debug("pausing play")
            self.mplayer.pause()
        self._save()

    def on_previous_track_down(self):
        """In this mode, the previous button pauses the currently playing song"""
        if self.current_track is not None:
            if self.mplayer.is_paused():
                self.personality.voice_library.say("Continuing with {}".format(self.current_track["name"]))
                self.mplayer.play()
            else:
                self.mplayer.pause()
                self.personality.voice_library.say("Pausing playlist, press the same button to continue")
                self._save()



    def on_next_track_down(self):
        logging.debug("LiveStreamState::next track")
        #self.mplayer.stop()
        self._play_next_track()
        #self.mplayer.next_track(self.play)
        self._save()

    def on_play_down(self):
        logging.debug("user requested to move to next state")
        if not self.mplayer.is_paused():
            logging.debug("pausing play")
            self.mplayer.pause()
        self._save()
        self.context.transition_to_next()

    def on_interrupt(self):
        self.mplayer.on_interrupt()
        self._save()
        self.state_is_interrupted = True

    def on_continue(self):
        self.mplayer.on_continue()
        self.state_is_interrupted = False

    def on_quit(self):
        self.mplayer.stop()
        self._save()

    def _say_track(self, track, seek_value):
        what_to_call_track = "track"
        if "word-for-track" in self.playlist_config:
            what_to_call_track = self.playlist_config["word-for-track"]
        if seek_value < 1:
            self.personality.voice_library.say("Next {} is {}".format(what_to_call_track, track["name"]))
        else:
            time_string = self.personality.voice_library.convert_seconds_to_saying(seek_value)
            self.personality.voice_library.say("Next {} is {} starting at {}".format(what_to_call_track, track["name"], time_string))



    def _play_next_track(self, track=None, seek_value=0):
        if self.mplayer.is_stopping():
            logging.debug("asked to play next track when mplayer was still stopping")
            time.sleep(3) # hack!

        if self.mplayer.is_playing():
            logging.debug("mplayer is playing, quick load")
            if track is None:
                track = self.get_next_track()
                seek_value = 0
            if track is None:
                self.on_empty_playlist()
            else:
                self.mplayer.pause()
                self._say_track(track, seek_value)
                self.mplayer.next_track(track["url"])
        elif self.mplayer.is_stopped():
            logging.debug("mplayer is stopped, long load")
            if track is None:
                track = self.get_next_track()
                seek_value = 0
            if track is None:
                self.on_empty_playlist()
            else:
                self._say_track(track, seek_value)
                self.mplayer.start(track["url"], seek_value)
        elif self.mplayer.is_paused():
            logging.debug("mplayer is paused, play")
            self.mplayer.play()

    def checkpoint(self):
        """
        Save user state every 5 seconds
        :return:
        """
        if self.mplayer.is_playing():
            if self.last_checkpoint is None:
                self._save()
                self.last_checkpoint = time.time()
            if time.time() - self.last_checkpoint > 5:
                self._save()
                self.last_checkpoint = time.time()

    def is_finished(self):
        self.checkpoint()
        if self.mplayer.is_finished():
            self.on_next_track_down()
        return False