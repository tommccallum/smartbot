from ability import Ability
from skills.voice import sayText


class TextToSpeech(Ability):
    """
    Send a text phrase to the Festival voice Text2Speech synthesizer
    """
    def __init__(self, text, personality, on_success=None, on_failure=None):
        super().__init__(on_success, on_failure)
        self.text = text
        self.personality = personality

    def perform(self):
        """Using the personality configuration say a phrase"""
        if self.text:
            print("[TextToSpeech] " + self.text)
            sayText(self.personality, self.text)
            return True
        return False
