import json
import os
import logging
import time

from actions import inline_action
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
        self.has_entry_completed = False
        self.mplayer = None

        # if we start this state and we need an internet connection then this
        # flag is set to True and the mplayer still not be started until we are
        # reconnected.
        self.play_on_hold_until_internet_is_back = False

        playlist = self.json
        if "playlist" in self.state_config:
            logging.debug("loading playlist from personality spec")
            playlist = self.state_config["playlist"]
        self.load_playlist(playlist)

    def get_mplayer(self):
        return self.configuration.context.mplayer

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
        self.playlist = Playlist([])
        if playlist_config:
            if not "tracks" in playlist_config:
                logging.error("no tracks key specified in playlist")
                logging.error(playlist_config)
                raise ValueError("no tracks key specified in playlist")
            self.playlist = Playlist(playlist_config["tracks"], self.configuration.HOME_DIRECTORY, self.configuration.get_config_path(), self.configuration.SMARTBOT_HOME)
            for s in self.playlist.playlist:
                if "name" not in s:
                    s["name"] = self.personality.voice_library.convert_filename_to_speech_text(s["url"])
            if "shuffle" in playlist_config:
                if playlist_config["shuffle"]:
                    self.playlist.shuffle()
            if "orderby" in playlist_config:
                self.playlist.sort(playlist_config["orderby"])
            if "start-track" in playlist_config:
                logging.debug("found start track, attempting to move position")
                if self.playlist.select_by_regex_only_if_earlier(playlist_config["start-track"]):
                    # poke these values in so we continue where we want to otherwise it will
                    # start at the NEXT track not this one.
                    self.json["user_state"] = { "track": self.playlist.get_current_track(), "seek": 0 }
                    logging.debug("setting user state to {}".format(self.json["user_state"]))


    def _save_state(self, values):
        """
        Save where the user got to on this
        :param values:
        :return:
        """
        values["user_state"] = {}
        if self.current_track and self.mplayer:
            values["user_state"]["track"] = self.current_track
            values["user_state"]["seek"] = self.get_mplayer().get_play_duration()
        #logging.debug("saving state as {}".format(values["user_state"]))
        return values

    def notify(self, event):
        super().notify(event)
        if event.id == EventEnum.DEVICE_RECONNECTED:
            self._restart_where_we_left_off()
        elif event.id == EventEnum.DEVICE_LOST:
            self.checkpoint(True)
            self.get_mplayer().stop()
        elif event.id == EventEnum.INTERNET_LOST:
            if self.current_track["url"][0:4] == "http":
                # looks as though when internet cuts out mplayer on pause can stay just fine.
                self.checkpoint(True)
                self.get_mplayer().pause()
                self.play_on_hold_until_internet_is_back = True
                inline_action("Sorry, the connection has been dropped.  Please hold.")
        elif event.id == EventEnum.INTERNET_FOUND:
            if self.current_track["url"][0:4] == "http":
                if self.play_on_hold_until_internet_is_back == True:
                    self.play_on_hold_until_internet_is_back = False
                    inline_action("Yay! The connection has been restored. Starting from where you left off.")
                    self._restart_where_we_left_off()
        elif event.id == EventEnum.ENTER_SLEEP_NOW:
            ## pause and stop immediately, without message to user
            self.on_previous_track_down()

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
        self._restart_where_we_left_off()
        self.has_entry_completed = True

    def _restart_where_we_left_off(self):
        # load an existing state if one exists
        seek = 0
        track = None
        # TM - no longer required once we are sharing an mplayer instance if not self.get_mplayer().is_paused():
        # if the mplayer is not paused then this must be a new session
        # so we want to load where we were last time for this mode
        # if we have a saved session that is
        user_state = self._get_user_state()
        if user_state is not None:
            if "seek" in user_state:
                seek = user_state["seek"]
            if "track" in user_state:
                logging.debug("restarting from a previous user state")
                track = user_state["track"]
                self.current_track = track
                self.playlist.set_current(track)
        self._play_next_track(track, seek)

    def on_exit(self):
        logging.debug("state exiting")
        if not self.get_mplayer().is_paused():
            logging.debug("pausing play")
            self.get_mplayer().pause()
        self._save()

    def on_previous_track_down(self):
        """In this mode, the previous button pauses the currently playing song"""
        if self.current_track is not None:
            if self.get_mplayer().is_paused():
                self.personality.voice_library.say("Continuing with {}".format(self.current_track["name"]))
                self.get_mplayer().play()
                self.active = True
            else:
                self.get_mplayer().pause()
                self.personality.voice_library.say("Pausing playlist, press the same button to continue")
                self._save()
                self.active = False



    def on_next_track_down(self):
        logging.debug("LiveStreamState::next track")
        #self.get_mplayer().stop()
        self.get_mplayer().pause()
        self._play_next_track()
        #self.get_mplayer().next_track(self.play)
        self._save()

    def on_play_down(self):
        logging.debug("user requested to move to next state")
        if not self.get_mplayer().is_paused():
            logging.debug("pausing play")
            self.get_mplayer().pause()
        self._save()
        ev = Event(EventEnum.TRANSITION_TO_NEXT)
        self.context.add_event(ev)

    def on_interrupt(self):
        self.get_mplayer().on_interrupt()
        self._save()
        self.state_is_interrupted = True

    def on_continue(self):
        ## cannot guarantee mplayer was asked to do something else
        self._restart_where_we_left_off()
        self.state_is_interrupted = False

    def on_quit(self):
        self.get_mplayer().stop()
        self._save()

    def _say_track(self, track, seek_value):
        logging.debug("announcing track")
        what_to_call_track = "track"
        announce_seek_time = True
        if "announce-seek" in self.state_config:
            announce_seek_time = self.state_config["announce-seek"]
        if "word-for-track" in self.playlist_config:
            what_to_call_track = self.playlist_config["word-for-track"]
        if announce_seek_time == False or seek_value < 1:
            inline_action("Next {} is {}".format(what_to_call_track, track["name"]))
        else:
            time_string = self.personality.voice_library.convert_seconds_to_saying(seek_value)
            inline_action("Next {} is {} starting at {}".format(what_to_call_track, track["name"], time_string))



    def _play_next_track(self, track=None, seek_value=0):
        if self.get_mplayer().is_stopping():
            logging.debug("asked to play next track when mplayer was still stopping")
            time.sleep(3) # hack!

        if track is None:
            track = self.get_next_track()
            seek_value = 0
        if track is None:
            self.on_empty_playlist()
        else:
            if not self.configuration.context.internet_detected:
                if track["url"][0:4] == "http":
                    inline_action("Sorry, the connection has been dropped.  Please hold.")
                    self.configuration.context.ignore_messages = False
                    return
            logging.debug("about to play next track...")
            # if self.get_mplayer().is_playing():
            #     logging.debug("mplayer is playing, quick load")
            #     self.get_mplayer().pause()
            self._say_track(track, seek_value)
                # self.get_mplayer().next_track(track["url"])
            # elif self.get_mplayer().is_stopped():
            #     logging.debug("mplayer is stopped, long load")
            #     self._say_track(track, seek_value)


            self.get_mplayer().start(track["url"], seek_value)
            # elif self.get_mplayer().is_paused():
            #     logging.debug("mplayer is paused, play")
            #     self.get_mplayer().play()

    def checkpoint(self, force=False):
        """
        Save user state every 5 seconds
        :return:
        """
        logging.debug("mplayer status: {}".format(self.get_mplayer().state))
        if self.get_mplayer().is_playing():
            if self.last_checkpoint is None or force:
                self._save()
                self.last_checkpoint = time.time()
            elif time.time() - self.last_checkpoint > 2:
                self._save()
                self.last_checkpoint = time.time()

    def is_finished(self):
        if not self.configuration.context.internet_detected:
            # if we start up and there is no connection then we
            # don't want to be testing if we are finished until
            # the internet is restored.
            if self.current_track["url"][0:4] == "http":
                return False
        self.checkpoint()
        if self.get_mplayer().is_finished():
            if self.playlist.size() > 0: # we want to stop it infinitely repeating its got no entries
                self.on_next_track_down()
        return False
