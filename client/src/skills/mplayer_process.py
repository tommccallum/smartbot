import json
import os
import logging
import signal
import subprocess
import time

import psutil

from app_context_lock import AppContextLock
from FifoFile import FifoFile
from skills.timer import Timer

class Player:
    """
    Base class of a player
    """
    def resume(self):
        pass

    def stop(self):
        pass

    def get_duration(self):
        pass

    def load(self, track, seek):
        pass

    def has_track_completed(self):
        pass


class MPlayerProcess(Player):
    """
    This object controls the actual mplayer process and fifo stack
    """
    def __init__(self, mplayer_config_path, fifo_directory):
        super().__init__()
        logging.debug("Creating MPlayerProcess object")
        self._init( mplayer_config_path, fifo_directory)

    def _init(self, mplayer_config_path, fifo_directory):
        self.audio_config = None
        self._load_config(mplayer_config_path)
        self.mplayer_command = self.audio_config["shell"]
        self.process = None
        self.timer = None
        self.fifo_file_prefix = "mplayer"
        self.fifo = FifoFile(fifo_directory, self.fifo_file_prefix)
        self.has_started = False

    def _load_config(self, file_path):
        """Set the mplayer config which is the same for all instances"""
        with open(file_path, "r") as config_fh:
            self.audio_config = json.load(config_fh)

    def resume(self):
        self.fifo.write(self.audio_config["commands"]["continue"])
        self.timer.resume()

    def stop(self):
        if self._is_alive():
            self.fifo.write(self.audio_config["commands"]["pause"])
        self.timer.stop()

    def play(self, track, seek):
        if self._is_alive():
            self.load(track, seek)
        else:
            self._start(track, seek)

    def get_duration(self):
        return self.timer.elapsedTime()

    def load(self, track, seek=0):
        """
        From mplayer slave commands:
        loadfile <file|url> <append>
        Load the given file/URL, stopping playback of the current file/URL.
            If <append> is nonzero playback continues and the file/URL is
            appended to the current playlist instead.
        """
        load_command = self.audio_config["commands"]["load"] + " \"{}\" 0".format(track)
        self.fifo.write(load_command)
        self._seek(seek)
        self.timer = Timer(seek)

    def has_track_completed(self):
        if self.has_started:
            return not self._is_alive()
        return False

    def _seek(self, value):
        if value > 0:
            seek_command = self.audio_config["commands"]["seek"]
            seek_command += " {} 2".format(value)
            self.fifo.write(seek_command)

    def _wait_for_mplayer_to_load(self):
        delay = 5
        if "start_delay" in self.audio_config:
            delay = self.audio_config["start_delay"]
        time.sleep(delay)

    def _start(self, track, seek=0):
        app_context_lock = AppContextLock()
        shell_cmd = self.mplayer_command
        shell_cmd = shell_cmd.replace("%fifo%", self.fifo.full_path)
        shell_cmd = shell_cmd.replace("%track%", track)
        if seek > 0:
            shell_cmd = shell_cmd.replace("%seek%", "-ss {}".format(int(seek)))
        else:
            shell_cmd = shell_cmd.replace("%seek%", "")
        logging.debug(shell_cmd)

        # if user wanted output to be diverted to a log file then do so otherwise do not
        # as its quite a lot of stuff not much use to anyone
        logfile = ""
        if "logfile" in self.audio_config:
            if self.audio_config["logfile"]:
                logfile = " > {} 2>&1".format(self.audio_config["logfile"])
        self.process = subprocess.Popen("exec {} {}".format(shell_cmd, logfile),
                                        shell=True,
                                        stdout=subprocess.PIPE,
                                        stderr=subprocess.PIPE)
        logging.info("PID of mplayer process:" + str(self.process.pid))
        self.timer = Timer(seek)
        self._wait_for_mplayer_to_load()
        self.has_started = True

    def _is_alive(self):
        """
        This is quite confusing.  We poll and this will clean up any zombie process that might still be around that
        will throw off our signal to the process.  We then send the 0 signal to our process and if it fails it will
        trigger an exception and we know that the process is dead.
        :return:
        """
        if self.process is None:
            if self.timer:
                self.timer.stop()
            return False
        try:
            self.process.poll()
            parent = psutil.Process(self.process.pid)
            for child in parent.children(recursive=True):
                os.kill(child.pid, 0)
            os.kill(parent.pid, 0)
            return True
        except:
            if self.timer:
                self.timer.stop()
            return False


    def _reset(self):
        # must close these otherwise terminal disappears when we quit
        # I think its because mplayer uses lots of escape sequences in output
        # which messes with the terminal
        os.system('stty sane')
        self.process = None
        self.fifo = None

    def _check_if_dead_via_shell_script(self):
        # we don't trust this so we are going to do a hacky shell check as well
        # we are looking for any mplayer processes that have our fifo file attached
        logging.debug("checking for any running mplayer processes with our fifo")
        cmd = "ps aux | grep mplayer | grep '{}' | grep -v grep | awk '{{print $2}}'".format(self.fifo)
        output = subprocess.check_output(cmd, shell=True)
        pids = output.decode("utf-8").split("\n")
        if len(pids) > 0:
            for pid in pids:
                if pid != "":
                    logging.debug("killing process {} as it should be dead".format(pid))
                    os.kill(int(pid), signal.SIGKILL)

    def _kill(self):
        try:
            self.process.poll()  # this will cause an exception is process is not available
            self.process.stderr.close()
            self.process.stdout.close()
            self.process.send_signal(signal.SIGINT)
            self.process.wait()
            self._check_if_dead_via_shell_script()
        except Exception as e:
            logging.debug(e)
        finally:
            self._reset()
        logging.info("Process should be dead")

    def __del__(self):
        logging.debug("Destroying MPlayerProcess object")
        self._kill()
