from ability import Ability
from skills.voice import sayText


class TextToSpeech(Ability):
    """
    Send a text phrase to the Festival voice Text2Speech synthesizer
    """
    def __init__(self, text, personality):
        self.text = text
        self.personality = personality

    def perform(self):
        """Using the personality configuration say a phrase"""
        if self.text:
            print("[TextToSpeech] " + self.text)
            sayText(self.personality, self.text)
