import json
import logging
import os
from pathlib import Path


class AppSettings:
    """Handles configuration"""
    HOME_DIRECTORY = str(Path.home())
    SMARTBOT_HOME = os.path.abspath(os.path.join(os.path.realpath(__file__), "..", "..", ".."))
    _DEFAULT_CONFIG_DIRECTORY = "smartbot"
    _DEFAULT_CONFIG_LOCATION = os.path.join(".config", _DEFAULT_CONFIG_DIRECTORY)
    _DEFAULT_CONFIG_NAME = "config.json"
    _instance = None
    _logging_setup = False
    DEFAULT_PERSONALITY_CONFIG_FILENAME = "personality.json"
    DEFAULT_DEVICES_CONFIG_FILENAME = "devices.json"
    DEFAULT_FIFO_DIRECTORY_NAME = "fifos"

    def __init__(self, user_specified_location=None, values = None):
        """Initialise Configuration

            config_location should be path to a file, by default config.json
            config_file is the absolute full path including filename
            config_path is just the filename
        """
        self.json = None
        logging.debug("Creating new configuration instance")
        if values:
            self.config_path = None
            self.config_file = None
            self.json = values
            logging.info("Using configuration given as parameter")
        else:
            self.config_path = os.path.join(AppSettings.HOME_DIRECTORY, AppSettings._DEFAULT_CONFIG_LOCATION)
            self.config_file = os.path.join(self.config_path, self._DEFAULT_CONFIG_NAME)
            if user_specified_location:
                self.config_file = None
                if os.path.isdir(user_specified_location):
                    self.config_file = os.path.join(user_specified_location, self._DEFAULT_CONFIG_NAME)
                else:
                    self.config_file = user_specified_location
                if not os.path.isfile(self.config_file):
                    raise FileNotFoundError(
                        "invalid configuration path or file specified ({})".format(user_specified_location))
                self.config_path = os.path.abspath(os.path.dirname(self.config_file))
                self.config_file = os.path.abspath(self.config_file)

            logging.info("Using configuration from '{}'".format(self.config_path))
            with open(self.config_file, "r") as in_file:
                self.json = json.load(in_file)

    def get_config_path(self):
        """Get the path where the configuration files are being kept"""
        return self.config_path

    def find(self, filename):
        """
        search for configuration file in known places
        returns the path, does not check if the path exists
        """
        if self.get_config_path() is None:
            return None
        full_path = filename
        if not os.path.sep in full_path:
            full_path = os.path.join(self.get_config_path(), filename)
        #if os.path.exists(full_path):
        return full_path
        #raise ValueError("could not locate path {}".format(filename))

    def get_fifo_path(self):
        full_path = self.find(AppSettings.DEFAULT_FIFO_DIRECTORY_NAME)
        if not full_path:
            full_path = os.path.join("/tmp",AppSettings.DEFAULT_FIFO_DIRECTORY_NAME)
        return full_path

    def get_devices_path(self):
        """
        Get filename for devices
        :return:
        """
        path = AppSettings.DEFAULT_DEVICES_CONFIG_FILENAME
        if "devices" in self.json:
            if "path" in self.json["devices"]:
                path = self.json["devices"]["path"]
        return self.find(path)

    def get_personality_path(self):
        """
        Get the path for the personality configuration.
        If the path is just a filename, we assume its in the same location as the configuration json file.
        Otherwise, we assume the full path is valid.
        The file path is checked and if the file does not exist then an FileNotFoundError exception is thrown.
        If no personality key-value pair in the configuration file then an ValueError exception is thrown.
        """
        path = AppSettings.DEFAULT_PERSONALITY_CONFIG_FILENAME
        if "personality" in self.json:
            path = self.json["personality"]
        return self.find(path)

    def get_media_path(self):
        return os.path.join(AppSettings.SMARTBOT_HOME, "media")

    def get_device(self):
        if "output" in self.json:
            if "device" in self.json["output"]:
                return self.json["output"]["device"]
        raise ValueError("\\output\\device does not exist in configuration")

    def __repr__(self):
        string_repr = json.dumps(self.json, sort_keys=True, indent=4)
        return string_repr


def create_app_settings(file_path: str = None):
    if file_path and not os.path.isfile(file_path):
        raise ValueError("configuration path '{}' does not exist".format(file_path))
    return AppSettings(file_path)


def create_app_settings_from_dict(the_values:dict):
    return AppSettings(values=the_values)

