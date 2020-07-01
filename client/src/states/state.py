import json
import logging
import os

import globalvars
from actions import inline_action
from bluetooth_speaker_handler import BluetoothSpeakerHandler
from event import Event, EventEnum

"""

States are used to handle what the user wants the device to do.

States can be in the main line, in which case they are specified in the 'states' key of the personality.json.
States can also be ephemeral and represent a Event callback, such as alarm_state or announce_state.
These ephemeral states are played and then removed from the play list. 

"""


class State(BluetoothSpeakerHandler):
    """
    This class should not be directly instantiated.
    """
    def __init__(self,
                 configuration: "Configuration",
                 personality: "Personality",
                 state_configuration
                 ):
        self.state_is_interrupted = False
        self._context = None
        self.title = None
        self.configuration = configuration
        self.personality = personality
        self.active = True          # set to False if we are not currently doing anything
        # this is the configuration in the 'states' key of the personality file
        self.state_config = state_configuration
        self.local_conf = None
        self.title = None
        self.json = {}
        if self.state_config is not None:
            if "filename" in self.state_config:
                self.local_conf = os.path.join(self.configuration.config_path, self.state_config["filename"])
                self._read()
        if "title" in self.state_config:
            self.title = self.state_config["title"]

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

    @property
    def context(self):
        return self._context

    @context.setter
    def context(self, context) -> None:
        self._context = context

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
        globalvars.app_context.add_event(ev)

    def on_previous_track_down(self):
        self.on_interrupt()
        inline_action("bye, see you later")
        ev = Event(EventEnum.TRANSITION_TO_NAMED)
        ev.data = self.state_config["on_end"]
        globalvars.app_context.add_event(ev)