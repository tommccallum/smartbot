"""
Configuration for the personality of the smart bot.
Anything that is different depending on the type of persona you are trying to project
should be part of this configuration.
"""
import json
import os


class PersonalitySettings:

    def __init__(self, data:dict):
        self.json = data

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

    def get_sleep_mode(self):
        if not "sleep" in self.json:
            return None
        return self.json["sleep"]

    def get_states(self):
        if not "states" in self.json:
            return None
        return self.json["states"]


def create_personality_settings(full_path:str):
    if full_path and not os.path.isfile(full_path):
        raise ValueError("{} does not exist".format(full_path))
    with open(full_path, "r") as in_file:
        data = json.load(in_file)
    return PersonalitySettings(data)

def create_personality_settings_from_dict(values:dict):
    return PersonalitySettings(values)

def write_personality_settings(full_path:str, obj : PersonalitySettings):
    with open(full_path, "w") as out_file:
        data = json.dumps(obj, sort_keys=T, index=4)
        out_file.write(data)