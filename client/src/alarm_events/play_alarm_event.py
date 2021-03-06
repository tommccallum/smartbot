import os
import logging
from skills.mplayer import MPlayer
from alarm_events.alarm_event import AlarmEvent


class PlayAlarmEvent(AlarmEvent):
    def __init__(self, data: object, config: "Configuration"):
        AlarmEvent.__init__(self, data)
        self.config = config
        self.mplayer = None

    def validate(self):
        # logging.debug(self.data)
        if "track" not in self.data:
            raise ValueError("track not found in data")
        if self.config.SMARTBOT_HOME is not None:
            self.data["track"] = self.data["track"].replace("%SMARTBOT%", self.config.SMARTBOT_HOME)
        if not os.path.isfile(self.data["track"]):
            raise ValueError("track '{}' not found".format(self.data["track"]))
        return True

    def begin_action(self):
        self.mplayer = MPlayer(self.config)
        self.mplayer.start(self.data["track"])

    def test_is_finished(self):
        return self.mplayer.is_finished()

    def on_finish(self):
        logging.debug("stopping alarm mplayer")
        self.mplayer.stop()
