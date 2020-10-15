

class Track:
    def __init__(self, track, seek):
        self.track = track
        self.seek = seek

    def dict(self):
        return { "url": self.track, "seek": self.seek }