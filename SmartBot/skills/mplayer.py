import os

from config_io import DEFAULT_CONFIG_LOCATION
from fifo import make_fifo


class MPlayer:
    STATE_PAUSED=0
    STATE_PLAYING=1

    def __init__(self):
        self.state = 0
        self.filename="mplayer.fifo"
        self.fifo = make_fifo(self.filename)

    def pause(self):
        if self.state == MPlayer.STATE_PLAYING:
            self._send_command_to(self.fifo, "cycle pause")
            self.state = MPlayer.STATE_PAUSED

    def play(self):
        if self.state == MPlayer.STATE_PAUSED:
            self._send_command_to(self.fifo, "cycle pause")

    def next_track(self):
        pass

    def previous_track(self):
        pass

    def _send_command_to(self, fifo, command):
        with open(fifo,"w") as out_file:
            out_file.write(command)

    def start(track):
        """Run mplayer and write pid to file just in case we need to clean up"""
        process = os.subprocess.run("mplayer --input-file in --framedrop decoder -vo null " + track)
        print("PID of mplayer process:"+process.pid)


def get_file_playlist():
    """Get all m4a files in Radio directory"""
    pass

def get_stream_playlist():
    """Get existing radio playlist"""
    pass


