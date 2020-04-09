import json
import os
import pathlib
from os import makedirs
from pathlib import Path
import shutil
from alarm import Alarm

DEFAULT_CONFIG_DIRECTORY="smartbot"
DEFAULT_CONFIG_LOCATION = os.path.join(".config",DEFAULT_CONFIG_DIRECTORY)
DEFAULT_CONFIG_NAME = "config.json"
HOME_DIRECTORY = str(Path.home())
CONFIG = None

def create_config(filename=None):
    global CONFIG
    if CONFIG:
        return CONFIG
    else:
        CONFIG = Configuration(filename)
    return CONFIG

class Configuration:
    """Handles configuration"""

    def __init__(self, config_file=None):
        self.alarm = None   # set when read new configuration
        self.context = None # set to allow the alarm to interrupt
        self.config = None
        self.config_path = os.path.join(HOME_DIRECTORY, DEFAULT_CONFIG_LOCATION)
        self.config_file = None
        self.json=None
        if config_file:
            self.config_file = config_file
            self.config_path = os.path.dirname(config_file)
        GLOBAL_CONFIG_PATH=self.config_path
        self._load()

    def _load(self):
        if self.config_file:
            if not os.path.isfile(self.config_file):
                raise FileNotFoundError("File '" + self.config_file + "' does not exist.")
        else:
            if not os.path.isdir(self.config_path ):
                src_conf_path = os.path.join(self._get_current_path(),"conf")
                shutil.copytree( src_conf_path, self.config_path)
            self.config_file = os.path.join(self.config_path, DEFAULT_CONFIG_NAME)
        if not os.path.isdir(os.path.join(self.config_path,"cache")):
            print("[INFO] Making cache file in "+os.path.join(self.config_path,"cache"))
            os.mkdir(os.path.join(self.config_path,"cache"))
        self._read()

    def _get_current_path(self):
        cpath = str(pathlib.Path(__file__).parent.absolute())
        return cpath

    def _read(self):
        with open(self.config_file, "r") as in_file:
            self.json = json.load(in_file)
        self.alarm = Alarm(self)

    def save(self):
        string_repr = json.dumps(self.json, sort_keys=True, indent=4)
        with open(self.config_file, "w") as out:
            out.write(string_repr)

    def get_personality_filepath(self):
        """
        Get the path for the personality configuration.
        If the path is just a filename, we assume its in the same location as the configuration json file.
        Otherwise, we assume the full path is valid.
        The file path is checked and if the file does not exist then an FileNotFoundError exception is thrown.
        If no personality key-value pair in the configuration file then an ValueError exception is thrown.
        """
        if "personality" in self.json:
            path = self.json["personality"]
            if not os.path.sep in path:
                path = os.path.join(self.config_path, path)
            if os.path.isfile(path):
                return path
            else:
                raise FileNotFoundError("Personality configuration '"+self.json["personality"]+"' does not exist.")
        raise ValueError("\\personality does not exist in general configuration.")

    def get_device(self):
        if "output" in self.json:
            if "device" in self.json["output"]:
                return self.json["output"]["device"]
        raise ValueError("\\output\\device does not exist in configuration")

    def __str__(self):
        string_repr = json.dumps(self.json, sort_keys=True, indent=4)
        return string_repr
