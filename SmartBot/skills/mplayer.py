import os
import subprocess
import signal

from config_io import DEFAULT_CONFIG_LOCATION
from fifo import make_fifo


class MPlayer:
    STATE_PAUSED=0
    STATE_PLAYING=1
    STATE_STOPPED=2

    def __init__(self):
        self.state = MPlayer.STATE_STOPPED
        self.filename="mplayer.fifo"
        self.fifo = make_fifo(self.filename)
        self.track = None

    def pause_or_play(self):
        if self.state == MPlayer.STATE_PLAYING or
            self.state == MPlayer.STATE_PAUSED:
            # note that for later versions of mplayer this changes to 'cycle pause'
            # so we need to handle the version of mplayer
            self._send_command_to(self.fifo, "pause")
            self.state = MPlayer.STATE_PAUSED
        elif self.state == MPlayer.STATE_STOPPED:
            self.play()

    def play(self, track=None):
        if self.state == MPlayer.STATE_PAUSED:
            self._send_command_to(self.fifo, "pause")
            self.state = MPlayer.STATE_PLAYING
        elif self.state == MPlayer.STATE_STOPPED:
            self.start(track)

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
            self.state = MPlayer.STATE_STOPPED

    def _send_command_to(self, fifo, command):
        with open(fifo,"w") as out_file:
            out_file.write(command+"\n")
            out_file.close()
            print("[INFO] Written "+command+" to "+fifo)

    def start(self, track=None):
        """Run mplayer and write pid to file just in case we need to clean up"""
        if track:
            self.track = track
        if self.track:
            # @todo locate mplayer on system directly
            self.process = subprocess.Popen("exec /usr/bin/mplayer --input-file \""+self.fifo+"\" --framedrop decoder -vo null \"" +self.track+"\"", shell=True, stdout=subprocess.PIPE)
            print("PID of mplayer process:"+str(self.process.pid))
            self.state = MPlayer.STATE_PLAYING


def get_file_playlist():
    """Get all m4a files in Radio directory"""
    pass

def get_stream_playlist():
    """Get existing radio playlist"""
    pass


