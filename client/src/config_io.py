import json
import logging
import os
import pathlib
import sys

from os import makedirs
from pathlib import Path
import shutil
from alarm import Alarm



class Configuration:
    """Handles configuration"""
    HOME_DIRECTORY = str(Path.home())
    SMARTBOT_HOME=os.path.abspath(os.path.join(os.path.realpath(__file__),"..","..",".."))
    _DEFAULT_CONFIG_DIRECTORY = "smartbot"
    _DEFAULT_CONFIG_LOCATION = os.path.join(".config", _DEFAULT_CONFIG_DIRECTORY)
    _DEFAULT_CONFIG_NAME = "config.json"
    _instance = None
    _logging_setup = False

    @staticmethod
    def get(path_to_config: str = None):
        if Configuration._instance is None:
            Configuration._instance = Configuration(path_to_config)
        return Configuration._instance

    @staticmethod
    def _setup_logging():
        if Configuration._logging_setup is False:
            root = logging.getLogger()
            root.setLevel(logging.DEBUG)
            handler = logging.StreamHandler(sys.stdout)
            handler.setLevel(logging.DEBUG)
            formatter = logging.Formatter('[%(module)s::%(funcName)s] [%(levelname)s] %(message)s')
            handler.setFormatter(formatter)
            root.addHandler(handler)
            Configuration._logging_setup = True

    @staticmethod
    def reset():
        if Configuration._instance is not None:
            me = Configuration.get()
            if me is not None:
                me._cleanup()
            Configuration._instance = None

    def __init__(self, config_location=None):
        """Initialise Configuration

            config_location should be path to a file, by default config.json
            config_file is the absolute full path including filename
            config_path is just the filename
        """
        Configuration._setup_logging()
        logging.debug("Creating new configuration instance")
        if config_location is not None:
            self.config_file = None
            if os.path.isfile(config_location):
                self.config_file = config_location
            elif os.path.isdir(config_location):
                if os.path.isfile(os.path.join(config_location,self._DEFAULT_CONFIG_NAME)):
                    self.config_file = os.path.join(config_location, self._DEFAULT_CONFIG_NAME)
            if self.config_file is None:
                raise FileNotFoundError("invalid configuration path or file specified ({})".format(config_location))
            self.config_path = os.path.dirname(self.config_file)
        else:
            self.config_path = os.path.join(Configuration.HOME_DIRECTORY, Configuration._DEFAULT_CONFIG_LOCATION)
            self.config_file = os.path.join(self.config_path, self._DEFAULT_CONFIG_NAME)

        # convert both to absolute paths
        self.config_path = os.path.abspath(self.config_path)
        self.config_file = os.path.abspath(self.config_file)
        logging.debug("Using configuration from {}".format(self.config_path))

        self.alarm = None           # set when read new configuration
        self.context = None         # set to allow the alarm to interrupt
        self.json = None            # the JSON from config.json
        self._load()

    def _cleanup(self):
        if self.alarm is not None:
            self.alarm.stop()
        path = self.get_config_path()
        if path is not None and path != "":
            if os.path.exists(os.path.join(path, "cache")):
                shutil.rmtree(os.path.join(path, "cache"))
            if os.path.exists(os.path.join(path, "fifos")):
                shutil.rmtree(os.path.join(path, "fifos"))

    def get_config_path(self):
        """Get the path where the configuration files are being kept"""
        return self.config_path

    def get_fifo_directory(self):
        return os.path.join(self.get_config_path(), "fifos")

    def get_devices_path(self):
        if "devices" in self.json:
            if "path" in self.json["devices"]:
                return  os.path.join(self.get_config_path(), self.json["devices"]["path"])
        return None

    def get_radio_path(self):
        if "radio_show_path" in self.json:
            return self.json["radio_show_path"]
        return None

    def get_music_path(self):
        if "music_path" in self.json:
            return self.json["music_path"]
        return None

    def find(self, filename):
        """search for configuration file in known places"""
        return os.path.join(self.get_config_path(), filename)

    def _load(self):
        if self.config_file is not None:
            if not os.path.isfile(self.config_file):
                raise FileNotFoundError("File '" + self.config_file + "' does not exist.")
        else:
            if not os.path.isdir(self.config_path):
                src_conf_path = os.path.join(self._get_current_path(), "conf")
                shutil.copytree(src_conf_path, self.config_path)
            self.config_file = os.path.join(self.config_path, Configuration._DEFAULT_CONFIG_NAME)
        if not os.path.isdir(os.path.join(self.config_path, "cache")):
            logging.debug("Making cache file in " + os.path.join(self.config_path, "cache"))
            os.mkdir(os.path.join(self.config_path, "cache"))
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
                raise FileNotFoundError("Personality configuration '" + self.json["personality"] + "' does not exist.")
        raise ValueError("\\personality does not exist in general configuration.")

    def get_device(self):
        if "output" in self.json:
            if "device" in self.json["output"]:
                return self.json["output"]["device"]
        raise ValueError("\\output\\device does not exist in configuration")

    def __str__(self):
        string_repr = json.dumps(self.json, sort_keys=True, indent=4)
        return string_repr

