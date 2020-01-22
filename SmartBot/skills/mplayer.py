import os
import subprocess
import signal

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

    def stop(self):
        if self.process:
            print("[INFO] Killing existing mplayer process ("+str(self.process.pid)+")")
            self.process.terminate()
            self.process.kill()
            print("[INFO] Process should be dead")

    def _send_command_to(self, fifo, command):
        with open(fifo,"w") as out_file:
            out_file.write(command)

    def start(self, track):
        """Run mplayer and write pid to file just in case we need to clean up"""
        # @todo locate mplayer on system directly
        self.process = subprocess.Popen("exec /usr/bin/mplayer --input-file \""+self.fifo+"\" --framedrop decoder -vo null \"" + track+"\"", shell=True, stdout=subprocess.PIPE)
        print("PID of mplayer process:"+str(self.process.pid))


def get_file_playlist():
    """Get all m4a files in Radio directory"""
    pass

def get_stream_playlist():
    """Get existing radio playlist"""
    pass


