import os

from abilities.console_printer import ConsolePrinter
from abilities.text_to_speech import TextToSpeech
from config_io import Configuration
from handler_state import HandlerState
import json

class IntroductionState(HandlerState):
    """
    A default state that is added after the final configured state to return us to the first.
    Its ONLY job should be to link restart the context loop.
    """

    @staticmethod
    def create(configuration: Configuration, personality: "Personality", state):
        return IntroductionState(configuration, personality, state)

    def __init__(self,
                 configuration: Configuration,
                 personality: "Personality",
                 state,
                 next_state: HandlerState = None) -> None:
        self.configuration = configuration
        self.personality = personality
        self.config = state
        self._next_state = next_state
        self.local_conf = os.path.join(self.configuration.config_path, "introduction.json")
        self.next_track = 0
        self.json = None
        self.completed = False
        self._read()

    def _read(self):
        if os.path.isfile(self.local_conf):
            with open(self.local_conf, "r") as conf:
                self.json = json.load(conf)

    def _save(self):
        with open(self.local_conf, "w") as conf:
            str = json.dumps(self.json, indent=4, sort_keys=True)
            conf.write(str)

    def on_enter(self):
        self._context.add(ConsolePrinter("IntroductionState::on_enter"))
        if not self.completed:
            self._context.add(TextToSpeech("Hello Innogen"))
            if not "introduction" in self.json:
                self._context.add(TextToSpeech("My name is "+self.personality.get_name()))
                self.json["introduction"] = True
            self._save()
            self.completed = True
        self.context.transition_to(self._next_state)
        self.context.execute()

    def on_exit(self):
        self._context.add(ConsolePrinter("IntroductionState::on_exit"))

