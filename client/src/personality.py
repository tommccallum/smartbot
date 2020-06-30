import json
import logging
import os
import datetime

import globalvars
from event import Event, EventEnum
from states.sleep_state import SleepState
from states_factory import StatesFactory
from voice_library import VoiceLibrary

class Personality:
    """
    Configuration for the personality of the smart bot
    """

    def __init__(self, config, file=None):
        self.config = config
        config.personality = self
        if file:
            self.file = file
        else:
            self.file = self.config.get_personality_filepath()
        self.json = None
        self._load()
        self.voice_library = VoiceLibrary(self)
        self.do_not_save = False

    def _load(self):
        if not os.path.isfile(self.file):
            raise FileNotFoundError("Personality file '{}' does not exist.".format(self.file))
        logging.info("Loading personality from '{}'".format(self.file))
        with open(self.file, "r") as in_file:
            self.json = json.load(in_file)
            if not "say" in self.json:
                self.json["say"] = {}
        self.check_sleep_spec_is_valid()

    def get_name(self):
        if not "name" in self.json or self.json["name"] == "":
            raise ValueError("No name specified for personality.")
        return self.json["name"]

    def get_voice(self):
        try:
            voice = self.json["conf"]["festival"]["voice"]
            return voice
        except:
            raise ValueError("\\conf\\festival\\voice not set in personality configuration")

    def get_language(self):
        try:
            language = self.json["conf"]["language"]
            return language
        except:
            raise ValueError("\\conf\\festival\\language not set in personality configuration")

    def set_states(self, states):
        self.json["states"] = states

    def get_states(self):
        return StatesFactory.create(self.config, self)

    def save(self):
        if self.do_not_save:
            logging.debug("not saving personality as do_not_save flag is True")
            return
        logging.debug("Saving bot personality to {}".format(self.file))
        str = json.dumps(self.json, sort_keys=True, indent=4)
        with open(self.file, "w") as out:
            out.write(str)

    def has_sleep_mode(self):
        return "sleep" in self.json

    def is_sleep_mode_enabled(self):
        """
        If has a sleep mode then we are enabled by default
        If sleep mode has a 'enabled' key then if this is true then enabled, otherwise its false
        :return:
        """
        if self.has_sleep_mode():
            if "enabled" in self.json["sleep"]:
                return self.json["sleep"]["enabled"] == True
            return True
        return False

    def get_hard_sleep_time(self):
        if "begin" in self.json["sleep"]:
            if type(self.json["sleep"]["begin"]) is dict:
                if "hard" in self.json["sleep"]["begin"]:
                    return self.json["sleep"]["begin"]["hard"]
            return self.json["sleep"]["begin"]
        return False

    def get_soft_sleep_time(self):
        if "begin" in self.json["sleep"]:
            if type(self.json["sleep"]["begin"]) is dict:
                if "soft" in self.json["sleep"]["begin"]:
                    return self.json["sleep"]["begin"]["soft"]
            return self.json["sleep"]["begin"]
        return False

    def get_end_sleep_time(self):
        if "end" in self.json["sleep"]:
            return self.json["sleep"]["end"]
        return False

    def get_on_end_sleep_action(self):
        if "on_end" in self.json["sleep"]:
            return self.json["sleep"]["on_end"]
        return False

    def check_sleep_spec_is_valid(self):
        if self.is_sleep_mode_enabled():
            if self.get_hard_sleep_time() == False:
                raise ValueError("No hard sleep value")
            if self.get_soft_sleep_time() == False:
                raise ValueError("No soft sleep value")
            if self.get_end_sleep_time() == False:
                raise ValueError("Sleep mode missing end key")
            if self.get_on_end_sleep_action() == False:
                raise ValueError("Sleep mode missing on_end key")
        return True

    def check_for_sleep_mode(self):
        """
        Checks to see if we are between the start and end of the sleep mode
        If we are then we may need to fire off an action to interrupt the current
        state.
        :return:    True if ought to be asleep
        """
        if not self.is_sleep_mode_enabled():
            return False
        when = datetime.datetime.now()
        today_as_string = when.strftime("%Y-%m-%d")
        end_time = datetime.datetime.strptime("{} {}".format(today_as_string, self.get_end_sleep_time()), "%Y-%m-%d %H:%M")
        soft_sleep = datetime.datetime.strptime("{} {}".format(today_as_string, self.get_soft_sleep_time()),
                                                "%Y-%m-%d %H:%M")
        hard_sleep = datetime.datetime.strptime("{} {}".format(today_as_string, self.get_hard_sleep_time()),
                                                "%Y-%m-%d %H:%M")
        if end_time < soft_sleep:
            end_time = end_time + datetime.timedelta(days=1)
        if globalvars.app_context and globalvars.app_context.is_asleep():
            if when > end_time:
                ev = Event(EventEnum.EXIT_SLEEP)
                ev.override_ignorable_events = True
                if globalvars.app_context:
                    globalvars.app_context.add_event( ev )
                return False
            return True
        else:
            if when > datetime.datetime.strptime("{} {}".format(today_as_string,self.get_end_sleep_time()), "%Y-%m-%d %H:%M"):
                return False
            if when >= hard_sleep:
                ev = Event(EventEnum.ENTER_SLEEP_NOW)
                ev.target_state = SleepState.create(self.config, self, {})
                if globalvars.app_context:
                    globalvars.app_context.add_event(ev)
                return True
            if when >= soft_sleep:
                ev = Event(EventEnum.ENTER_SLEEP_IF_ABLE)
                ev.target_state = SleepState.create(self.config, self, {})
                if globalvars.app_context:
                    globalvars.app_context.add_event(ev)
                return True
            return False