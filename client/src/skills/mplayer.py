import os
import signal
import subprocess
import psutil
import json
from fifo import make_fifo
import time
import logging


class MPlayer:
    instance_counter = 1
    """Used to get unique MPlayer fifo"""
    STATE_PAUSED = 0
    STATE_NOT_READY = 4
    STATE_PLAYING = 1
    STATE_STOPPED = 2
    STATE_STOPPING = 3

    def __init__(self, configuration):
        self.instance_id = MPlayer.instance_counter
        MPlayer.instance_counter += 1
        self.configuration = configuration
        self.config = None
        self.fifo = None
        self.track = None
        self.mplayer_process = None
        self.state = MPlayer.STATE_STOPPED
        self.last_start_play = None
        self.play_duration = 0       # how much time we have spent in play
        self._load_config()


    def __del__(self):
        if not self.mplayer_process is None:
            self._stop_and_clean_up()

    def start_play_timer(self):
        """
        Resets play duration AND sets timer
        :return:
        """
        self.play_duration = 0
        self.last_start_play = time.time()

    def continue_play_timer(self):
        """
        Continues timer, but does not reset play_duration
        :return:
        """
        self.last_start_play = time.time()

    def set_play_duration(self, value):
        """
        Set the duration to a specific value
        :param value:
        :return:
        """
        self.play_duration = value

    def stop_play_timer(self):
        """
        Stop play timer and get value
        :return:
        """
        duration = time.time() - self.last_start_play
        self.play_duration += duration
        return self.play_duration

    def get_play_duration(self):
        """
        Get current duration we have played for
        :return:
        """
        duration = time.time() - self.last_start_play
        return self.play_duration + duration


    def _load_config(self):
        """Set the mplayer config which is the same for all instances"""
        config_path = self.configuration.find("mplayer.json")
        with open(config_path, "r") as config_fh:
            self.config = json.load(config_fh)

    def on_interrupt(self):
        logging.info("[INFO] mplayer object interrupted")
        self.pause()

    def on_continue(self):
        logging.info("[INFO] mplayer object continue")
        self.play()

    def is_playing(self):
        return self.state == MPlayer.STATE_PLAYING

    def is_paused(self):
        return self.state == MPlayer.STATE_PAUSED

    def is_stopped(self):
        return self.state == MPlayer.STATE_STOPPED

    def is_stopping(self):
        return self.state == MPlayer.STATE_STOPPING

    def is_finished(self):
        """check if process has completed"""
        #        return self.process == None or self.process.poll() == None
        if self.state == MPlayer.STATE_NOT_READY:
            # setting up still
            return False
        if self.mplayer_process is None:
            self.state = MPlayer.STATE_STOPPED
            return True
        try:
            # at end mplayer stays as a zombie process - why?
            logging.debug("Test if exec and mplayer are finished")
            self.mplayer_process.poll()
            parent = psutil.Process(self.mplayer_process.pid)
            for child in parent.children(recursive=True):
                logging.debug("testing child {}-{}".format(child.ppid,child.pid))
                os.kill(child.pid, 0)
            os.kill(parent.pid,0)
            logging.debug("{} exists".format(self.mplayer_process.pid))
        except:
            logging.debug("{} does not exist".format(self.mplayer_process.pid))
            self.state = MPlayer.STATE_STOPPED
            return True     # pid does not exist
        return False    # pid does exist

    def play(self, track=None):
        if self.state == MPlayer.STATE_PAUSED:
            self._send_command_to(self.config["commands"]["continue"])
            self.state = MPlayer.STATE_PLAYING
            self.continue_play_timer()
        elif self.state == MPlayer.STATE_STOPPING:
            logging.debug("mplayer caught in stopping state, not sure what will happen here...")
        elif self.state == MPlayer.STATE_STOPPED:
            self.start(track)

    def stop(self):
        self.state = MPlayer.STATE_STOPPING
        if self.mplayer_process:
            self._stop_and_clean_up()
            logging.info("Process should be dead")
        self.state = MPlayer.STATE_STOPPED
        self.stop_play_timer()

    def seek(self, value):
        """
        seek absolute amount from start
        """
        if self.mplayer_process is None:
            raise Exception("mplayer process must be loaded first, before seek")
        seek_command = self.config["commands"]["seek"]
        seek_command += " {} 2".format(value)
        self._send_command_to(seek_command)
        self.set_play_duration(value)
        self.continue_play_timer()

    def next_track(self, track:str):
        """
        As we are controlling the playlist, we just have to stop and restart the
        mplayer
        """
        if self.mplayer_process is None:
            raise Exception("mplayer process must be loaded first, before load")
        load_command = self.config["commands"]["load"]+" \"{}\" 0".format(track)
        self._send_command_to(load_command)
        self.start_play_timer()

    def pause(self):
        if self.state != MPlayer.STATE_PAUSED:
            self.state = MPlayer.STATE_PAUSED
            logging.debug("pausing mplayer")
            self._send_command_to(self.config["commands"]["pause"])
            self.stop_play_timer()


    # def pause_or_play(self):
    #     if self.state == MPlayer.STATE_PLAYING:
    #         self.state = MPlayer.STATE_PAUSED
    #         logging.debug("pausing mplayer")
    #         self._send_command_to(self.config["commands"]["pause"])
    #     else:
    #         # note that for later versions of mplayer this changes to 'cycle pause'
    #         # so we need to handle the version of mplayer
    #         logging.debug("unpausing mplayer")
    #         self.play()

    def _stop_and_clean_up(self):
        try:
            if self.mplayer_process is not None:
                logging.debug("polling process to see if it has finished")
                self.mplayer_process.poll() # this will cause an exception is process is not available
                logging.debug("Shutting down stderr and stdout")
                self.mplayer_process.stderr.close()
                self.mplayer_process.stdout.close()
                logging.debug("terminating process politely")
                self.mplayer_process.send_signal(signal.SIGINT)
                logging.debug("waiting for process to complete")
                self.mplayer_process.wait()
        except Exception as e:
            logging.debug(e)
        finally:
            # must close these otherwise terminal disappears when we quit
            # I think its because mplayer uses lots of escape sequences in output
            # which messes with the terminal
            os.system('stty sane')
            self.mplayer_process = None
            logging.debug("attempting to remove fifo {}".format(self.fifo))
            if self.fifo and os.path.exists(self.fifo):
                logging.debug("Removing {}".format(self.fifo))
                os.remove(self.fifo)


    def _send_command_to(self, command):
        logging.debug("Sending command '{}' to fifo '{}'".format(command,self.fifo))
        if self.fifo is None:
            logging.debug("fifo is set to None, ignoring")
            return
        if os.path.exists(self.fifo):
            with open(self.fifo, "w") as out_file:
                out_file.write(command + "\n")
                out_file.close()
                logging.info("Written '" + command + "' to " + self.fifo)
        else:
            logging.debug("fifo {} does not exist".format(self.fifo))

    def _make_fifo(self):
        fifo_filename = "mplayer_" + str(self.instance_id) + ".fifo"
        self.fifo = make_fifo(self.configuration, fifo_filename)

    def _start_mplayer_and_play_track(self, track, seek):
        """
        Starts mplayer process for playing track

        Stores process info self.mplayer_process
        Creates fifo file on startup with unique pid
        """
        logging.debug("{} {}".format(track,seek))
        self._make_fifo()
        shell_cmd = self.config["shell"]
        shell_cmd = shell_cmd.replace("%fifo%", self.fifo)
        shell_cmd = shell_cmd.replace("%track%", track)
        if seek > 0:
            shell_cmd = shell_cmd.replace("%seek%", "-ss {}".format(int(seek)))
        else:
            shell_cmd = shell_cmd.replace("%seek%", "")
        logging.debug(shell_cmd)
        if self.mplayer_process:
            self.stop()
        self.mplayer_process = subprocess.Popen("exec "+shell_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        logging.info("PID of mplayer process:" + str(self.mplayer_process.pid))
        self.state = MPlayer.STATE_PLAYING
        # mplayer is quite slow to start so
        # so wait before we execute anything else
        time.sleep(2)
        if seek > 0:
            self.set_play_duration(seek)
            self.continue_play_timer()
        else:
            # we do this afterwards as we would rather be too little duration than too much
            self.start_play_timer()

    def start(self, track=None, seek=0):
        """Run mplayer and write pid to file just in case we need to clean up"""
        self.state = MPlayer.STATE_NOT_READY
        if track:
            self.track = track
        if self.track:
            self._start_mplayer_and_play_track( self.track, seek )


