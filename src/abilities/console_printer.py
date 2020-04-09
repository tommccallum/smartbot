from ability import Ability


class ConsolePrinter(Ability):
    """
    Used to output status messages to the console
    """

    INFO=0
    DEBUG=1

    def __init__(self, text, level=INFO, on_success=None, on_failure=None):
        super().__init__(on_success, on_failure)
        self.text = text
        self.level = level

    def _get_level(self):
        if self.level == ConsolePrinter.DEBUG:
            return "DEBUG"
        else:
            return "INFO"

    def perform(self):
        if not self.text:
            print("[WARNING] no text was found in object")
        else:
            print("["+self._get_level()+"] "+self.text)
            return True
        return False