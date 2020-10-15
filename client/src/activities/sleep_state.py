import logging
import random
import datetime

from actions import inline_action, expand_path
from activities.activity import Activity
from event import Event, EventEnum
from skills.audio_player import AudioPlayer


class SleepState(Activity):
    """
    A state that is active during the sleep period

    Logic:

    When sleep time hit, if the current state is paused we replace it with this state.
    When user hits any +/- button then it says the time (not date)!
    When user hits play, we replace with the last state being played??
    """
    def __init__(self,
                 app_state,
                 state_configuration
                 ) -> None:
        super().__init__(app_state, state_configuration)
        self.next_track = 0
        self.first_run = True
        self.state_config = self.personality().json["sleep"]
        self.audio_player = None

    def notify(self, event: Event):
        super().notify(event)
        if event.id == EventEnum.EXIT_SLEEP:
            logging.debug("attempting to leave sleep state")
            if "on_end" in self.state_config:
                ev = Event(EventEnum.TRANSITION_TO_NAMED)
                ev.data = self.state_config["on_end"]
            else:
                ev = Event(EventEnum.TRANSITION_TO_FIRST)
            ev.override_ignorable_events = True
            self.add_event(ev)
            # @todo what happens when we wake up and no one is around???

    def on_enter(self):
        logging.debug("SleepState::on_enter")
        self.play_sleepy_music()

    def play_sleepy_music(self):
        music = None
        if "on_enter" in self.state_config:
            music = expand_path(self.state_config["on_enter"])
        if not music:
            return
        if self.mplayer:
            if self.mplayer.is_finished():
                self.mplayer.start(music)
            elif self.mplayer.is_paused():
                self.mplayer.play()
        else:
            logging.debug("Starting sleepy music '{}'".format(music))
            self.audio_player = AudioPlayer(self.config())
            self.audio_player.play(music)

    def on_exit(self):
        logging.debug("SleepState::on_exit")
        if self.audio_player:
            self.audio_player.stop()


    def is_finished(self):
        if self.audio_player and self.audio_player.is_finished():
            self.audio_player.stop()
            self.audio_player = None
        return False

    def on_previous_track_down(self):
        # say something
        if self.audio_player:
            self.audio_player.pause()
        saying = random.choice(self.state_config["phrases"])
        saying = saying.replace("%T", datetime.datetime.now().strftime("%H:%M"))
        inline_action(saying)
        self.play_sleepy_music()

    def on_next_track_down(self):
        # say something
        # say something
        if self.audio_player:
            self.audio_player.pause()
        saying = random.choice(self.state_config["phrases"])
        saying = saying.replace("%T", datetime.datetime.now().strftime("%H:%M"))
        inline_action(saying)
        self.play_sleepy_music()


    def on_play_down(self):
        # say something
        if self.audio_player:
            self.audio_player.pause()
        saying = random.choice(self.state_config["phrases"])
        saying = saying.replace("%T", datetime.datetime.now().strftime("%H:%M"))
        inline_action(saying)
        if self.audio_player:
            self.audio_player.play()

    def is_sleep_state(self):
        return True

