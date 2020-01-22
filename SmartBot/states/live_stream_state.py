from abilities.console_printer import ConsolePrinter
from abilities.text_to_speech import TextToSpeech
from config_io import Configuration
from handler_state import HandlerState


class LiveStreamState(HandlerState):
    @staticmethod
    def create(configuration: Configuration, personality: "Personality"):
        return LiveStreamState(configuration, personality)

    def __init__(self, configuration: Configuration, personality: "Personality",
                 next_state: HandlerState = None) -> None:
        self.configuration = configuration
        self.personality = personality
        self._next_state = next_state

    def set_next_state(self, next):
        self._next_state = next

    def on_enter(self):
        self._context.add(ConsolePrinter("RadioState::on_enter"))

    def on_exit(self):
        self._context.add(ConsolePrinter("RadioState::on_exit"))

    def on_previous_track_down(self):
        self.context.add(TextToSpeech("Pausing radio"))

    def on_previous_track_up(self):
        # self.context.add(mplayer_pause())
        self.context.execute()

    def on_next_track_down(self):
        self.context.add(TextToSpeech("Next show"))

    def on_next_track_up(self):
        self.context.execute()

    def on_play_down(self):
        self.context.add(TextToSpeech("Pausing radio"))
        self.context.transition_to(self._next_state)
        self.context.execute()

    def on_play_up(self):
        pass
