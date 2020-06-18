import json
import logging
import os

from states_factory import StatesFactory
from voice_library import VoiceLibrary


class Personality:
    """
    Configuration for the personality of the smart bot
    """

    def __init__(self, config, file=None):
        self.config = config
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
        logging.debug("Loading bot personality from {}".format(self.file))
        with open(self.file, "r") as in_file:
            self.json = json.load(in_file)
            if not "say" in self.json:
                self.json["say"] = {}

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
