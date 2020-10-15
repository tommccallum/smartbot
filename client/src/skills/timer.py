import time

class Timer:
    """
    Timer used for recording how long a track has played for (in seconds)
    Starts on creation of object
    """
    def __init__(self, value=0):
        self.duration = value
        self.start_time = None
        self.end_time = None
        self.resume()

    def resume(self,now=None):
        self.start_time = time.time()
        self.end_time = None

    def stop(self):
        if self.end_time != None: return self.duration
        self.end_time = time.time()
        self.duration += self.end_time - self.start_time

    def elapsedTime(self):
        if self.end_time:
            return int(self.duration)
        return int(self.duration + (time.time() - self.start_time))

    def __repr__(self):
        return "{} {} {}".format(self.start_time, self.end_time, self.duration)