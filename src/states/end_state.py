from abilities.console_printer import ConsolePrinter
from handler_state import HandlerState


class EndState(HandlerState):
    """
    A default state that is added after the final configured state to return us to the first.
    Its ONLY job should be to link restart the context loop.
    """
    def __init__(self):
        pass

    def on_enter(self):
        self._context.add(ConsolePrinter("EndState::on_enter"))
        self._context.transition_to_first()

    def on_exit(self):
        self._context.add(ConsolePrinter("EndState::on_exit"))

