import json
import logging

from skills.mplayer_process import MPlayerProcess


class Mode:
    """
    Each state of the audio player
    """
    def __init__(self, audio_player):
        self.audio_player = audio_player

    def name(self):
        pass

    def play(self, track, seek):
        pass

    def pause(self):
        pass

    def stop(self):
        pass

    def has_track_completed(self):
        if self.audio_player and self.audio_player.mplayer_process():
            return self.audio_player.mplayer_process().has_track_completed()
        return False


class PlayingMode(Mode):
    def __init__(self, audio_player):
        super().__init__(audio_player)

    def name(self):
        return "playing"

    def play(self, track, seek):
        self.audio_player.track = track
        self.audio_player.load(track, seek)
        return self

    def pause(self):
        self.audio_player.mplayer_process().stop()
        self.audio_player.seek = self.audio_player.mplayer_process().get_duration()
        return PauseMode(self.audio_player)

    def stop(self):
        self.audio_player.mplayer_process().stop()
        self.audio_player.duration = self.audio_player.mplayer_process().get_duration()
        return StartMode(self.audio_player)


class PauseMode(Mode):
    """
    The mode is ACTIVE when we are paused.
    """
    def __init__(self, audio_player):
        super().__init__(audio_player)

    def name(self):
        return "paused"

    def play(self, track, seek):
        if self.audio_player.track == track:
            self.audio_player.mplayer_process().resume()
        else:
            self.audio_player.mplayer_process().play(self.audio_player.track, self.audio_player.seek)
        return PlayingMode(self.audio_player)

class StartMode(Mode):
    """
    ACTIVE when object is first run
    """
    def __init__(self, audio_player):
        super().__init__(audio_player)

    def name(self):
        return "start"

    def play(self, track, seek):
        self.audio_player.mplayer_process().play(track,seek)
        return PlayingMode(self.audio_player)


class AudioPlayer:
    """
    We have a single instance of the mplayer that we switch tracks on
    this is more stable and quicker than constantly killing and loading
    mplayer processes.
    """
    def __init__(self, app_state):
        self.app_state = app_state
        self.audio_player_config = None
        self.track = None
        self.seek = None
        self.current_mode = StartMode(self)
        logging.debug("creating audio_player object {}".format(self.__hash__))

    def __del__(self):
        logging.debug("deleting audio_player object")

    def mplayer_process(self):
        return self.app_state.context.mplayer_process(self)

    def on_interrupt(self):
        logging.info("[INFO] mplayer object interrupted")
        self.pause()

    def on_continue(self):
        logging.info("[INFO] mplayer object continue")
        self.resume()

    def is_playing(self):
        return type(self.current_mode) == PlayingMode

    def is_paused(self):
        return type(self.current_mode) == PauseMode

    def is_stopped(self):
        return type(self.current_mode) == StartMode

    def has_track_completed(self):
        """check if process has completed"""
        if self.app_state.context.mplayer_is_owner(self):
            if self.current_mode.has_track_completed():
                self.current_mode = StartMode(self)
                return True
        return False

    def play(self, track=None, seek = 0):
        self.app_state.context.mplayer_capture(self)
        self.current_mode = self.current_mode.play(track, seek)

    def pause(self):
        self.current_mode = self.current_mode.pause()
        self.app_state.context.mplayer_release(self)

    def resume(self):
        self.app_state.context.mplayer_capture(self)
        self.current_mode = self.current_mode.play(self.track, self.seek)

    def stop(self):
        self.current_mode = self.current_mode.stop()
        self.app_state.context.mplayer_release(self)



