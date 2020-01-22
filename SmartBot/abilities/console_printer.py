from ability import Ability


class ConsolePrinter(Ability):
    """
    Used to output status messages to the console
    """

    INFO=0
    DEBUG=1

    def __init__(self, text, level=INFO):
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