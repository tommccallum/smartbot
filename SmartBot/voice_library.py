import hashlib
import os


class VoiceLibrary:
    """Stores the voice wav files"""

    def __init__(self, personality: "Personality"):
        self.personality = personality
        self.json = self.personality.json["say"]

    def has_saying(self, text):
        try:
            return True
        except:
            return False

    def get_saying(self, text):
        try:
            return self.json[text]
        except:
            return None

    def get_saying_path(self, text):
        m = hashlib.sha256()
        m.update(text.encode('utf-8'))
        name = m.hexdigest() + ".wav"
        file_path = os.path.join("cache", name)
        file_path = os.path.join(self.personality.config.config_path, file_path)
        return file_path

    def save_saying(self, text, file_path):
        self.json[text] = file_path
        self.personality.save()
