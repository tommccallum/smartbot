"""
Holds current state and is referenced via the global variable
Allows for us to easily load a new set of configurations during runtime.
"""
import logging

from activity_factory import create_activities
from app_context_lock import AppContextLock
from app_settings import AppSettings, create_app_settings, create_app_settings_from_dict
from personality_settings import create_personality_settings, create_personality_settings_from_dict
from sleep_mode import SleepMode
from user_context import UserContext
from voice_library import VoiceLibrary


class AppState:
    @staticmethod
    def create_from_file(settings_full_path=None):
        settings = create_app_settings(settings_full_path)
        return AppState(settings)

    @staticmethod
    def create_from_dict(values: dict):
        if "config" not in values:
            raise AttributeError("'config' key not found in dictionary")
        settings = create_app_settings_from_dict(values["config"])
        return AppState(settings, values)

    def __init__(self,
                 app_settings: AppSettings,
                 the_dev_specified_configuration: dict = None  # use this to poke in values for testing
                 ):
        self.dev_specified_configuration = the_dev_specified_configuration
        self.settings = app_settings
        self.personality = None
        self.voice_library = None
        self.context = None
        self.sleep_mode = None
        self._load_dependent_configurations()

    def _load_dependent_configurations(self):
        if self.dev_specified_configuration:
            if "personality" not in self.dev_specified_configuration:
                return
            self.personality = create_personality_settings_from_dict(self.dev_specified_configuration["personality"])
        else:
            self.personality = create_personality_settings(self.settings.get_personality_path())
        self.voice_library = VoiceLibrary(self)
        self.activities = create_activities(self)
        self.sleep_mode = SleepMode(self)
        self.context = UserContext(self, self.activities)

    def capabilities(self):
        return self.context.capabilities

    def reload(self, the_dev_specified_configuration = None):
        self.context.stop()
        AppContextLock()
        if the_dev_specified_configuration:
            self.dev_specified_configuration = the_dev_specified_configuration
            self.settings = create_app_settings_from_dict(the_dev_specified_configuration)
        else:
            self.settings = create_app_settings(self.settings.config_file)
        self._load_dependent_configurations()
        self.context.start()

    def has_dict(self, key : str):
        if self.dev_specified_configuration:
            if key in self.dev_specified_configuration:
                return self.dev_specified_configuration[key]
        return None