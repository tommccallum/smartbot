import json
import logging
import os

from actions import inline_action
from bluetooth_speaker_handler import BluetoothSpeakerHandler
from event import Event, EventEnum

"""

States are used to handle what the user wants the device to do.

States can be in the main line, in which case they are specified in the 'states' key of the personality.json.
States can also be ephemeral and represent a Event callback, such as alarm_state or announce_state.
These ephemeral states are played and then removed from the play list. 

"""


class Activity(BluetoothSpeakerHandler):
    """
    This class should not be directly instantiated.
    """
    def __init__(self,
                 app_state,
                 state_configuration
                 ):
        if not app_state:
            raise ValueError("missing application state from activity")
        if not app_state.voice_library:
            raise ValueError("missing voice component, not loading {}".format(state_configuration["title"]))

        self.state_is_interrupted = False
        self.app_state = app_state
        self.title = None
        self.active = True          # set to False if we are not currently doing anything
        # this is the configuration in the 'states' key of the personality file
        self.state_config = state_configuration
        if "title" in self.state_config:
            self.title = self.state_config["title"]
        self.local_conf = None
        self.title = None
        self.json = None
        self._load_local_settings()

    def _load_local_settings(self):
        if self.state_config is not None:
            if "filename" in self.state_config:
                config_path = self.app_state.settings.get_config_path()
                if config_path:
                    self.local_conf = os.path.join(config_path, self.state_config["filename"])
                    self._read()
                else:
                    self.json = self.app_state.has_dict(self.state_config["filename"])
                    if not self.json:
                        self.json = self.app_state.has_dict(self.state_config["title"])
            else:
                self.json = self.app_state.has_dict(self.state_config["title"])
        if self.json is None:
            self.json = {}

    def settings(self):
        return self.app_state.settings

    def personality(self):
        return self.app_state.personality

    def voice(self):
        return self.app_state.voice_library

    def add_event(self, event):
        if self.app_state.context:
            self.app_state.context.add_event(event)

    def audio_player(self):
        if self.app_state.context:
            return self.app_state.context.audio_player()
        return None

    def _read(self):
        logging.debug(self.local_conf)
        if os.path.isfile(self.local_conf):
            with open(self.local_conf, "r") as conf:
                self.json = json.load(conf)

    def _save(self):
        if self.local_conf is None:
            return
        if self.json is None:
            return
        self.json = self._save_state(self.json)
        with open(self.local_conf, "w") as conf:
            str = json.dumps(self.json, indent=4, sort_keys=True)
            conf.write(str)

    def _save_state(self, values):
        """
        Override with your own settings
        """
        return values

    def _get_user_state(self):
        if self.json is not None:
            if "user_state" in self.json:
                return self.json["user_state"]
        return None

    def notify(self, event: Event):
        """Purely the receiver of events from context"""
        if event.id == EventEnum.ENTER_OWNER:
            self.on_continue()
        elif event.id == EventEnum.EXIT_OWNER:
            self.on_interrupt()
        elif event.id == EventEnum.QUIT:
            self.on_quit()

    def run(self):
        if self.state_is_interrupted:
            self.on_continue()
        else:
            self.on_enter()

    def on_enter(self):
        """on entering this new state"""
        pass

    def on_exit(self):
        """on transitioning from this state"""
        pass

    def on_interrupt(self):
        pass

    def on_continue(self):
        pass

    def on_quit(self):
        pass

    def is_finished(self):
        return False

    def is_sleep_state(self):
        return False

    def is_active(self):
        return self.active

    def on_next_track_down(self):
        self.on_interrupt()
        inline_action("bye, see you later")
        ev = Event(EventEnum.TRANSITION_TO_NAMED)
        ev.data = self.state_config["on_end"]
        self.app_state.context.add_event(ev)

    def on_previous_track_down(self):
        self.on_interrupt()
        inline_action("bye, see you later")
        ev = Event(EventEnum.TRANSITION_TO_NAMED)
        ev.data = self.state_config["on_end"]
        self.app_state.context.add_event(ev)