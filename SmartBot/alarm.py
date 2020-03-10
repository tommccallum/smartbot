import os

import schedule
import time
import re
from datetime import datetime
import threading

from skills.mplayer import MPlayer


class Alarm:
    """Alarm class to handle scheduling tasks"""

    def __init__(self, config_object):
        self.config_object = config_object
        self.schedule()

    def schedule(self):
        schedule.clear()
        #schedule.every(1).minutes.do(lambda: self.wakeup("test", None))
        if "alarms" in self.config_object.json:
            for alarm in self.config_object.json["alarms"]:
                at = alarm["when"]
                if type(at) is not list:
                    at = [ at ]
                action = alarm["action"]
                args = alarm["args"]
                self.schedule_task(at, action, args)
                schedule.run_pending()
                print("Next job to run at ",str(schedule.next_run()))
            self.timer()

    def timer(self):
        schedule.run_pending()
        threading.Timer(1,self.timer).start()

    def check_args(self, action, args):
        if action == "play":
            if not os.path.isfile(args[0]):
                raise ValueError(str(args[0])+"does not exist")
            return
        raise ValueError("invalid action specified for alarm")

    def schedule_task(self, at_list, action, args):
        self.check_args( action, args )
        days = []
        time_of_day = None
        time_pattern = re.compile("\d{1,2}:\d\d")

        for at_item in at_list:
            if time_pattern.match(at_item):
                time_of_day = at_item
            else:
                if at_item == "weekdays":
                    days = [1,2,3,4,5]
                elif at_item == "weekend":
                    days = [6,0]

        print("[INFO] Setting alarm for days ", str(days), " at ", time_of_day, " for action ", action, " ", str(args))

        if time_of_day is not None:
            for day in days:
                if day == 0:
                    schedule.every().sunday.at(time_of_day).do(lambda: self.wakeup(action, args))
                elif day == 1:
                    schedule.every().monday.at(time_of_day).do(lambda: self.wakeup(action, args))
                elif day == 2:
                    schedule.every().tuesday.at(time_of_day).do(lambda: self.wakeup(action, args))
                elif day == 3:
                    schedule.every().wednesday.at(time_of_day).do(lambda: self.wakeup(action, args))
                elif day == 4:
                    schedule.every().thursday.at(time_of_day).do(lambda: self.wakeup(action, args))
                elif day == 5:
                    schedule.every().friday.at(time_of_day).do(lambda: self.wakeup(action, args))
                elif day == 6:
                    schedule.every().saturday.at(time_of_day).do(lambda: self.wakeup(action, args))

    def wakeup(self, action, args):
        now = datetime.now()
        date_time = now.strftime("%Y-%m-%d %H:%M:%S")
        print("[ALARM] Woke at ", date_time, " to ", action, " ", str(args))
        if action == "play":
            self.config.context.on_interrupt()
            mplayer = MPlayer()
            mplayer.start(args[0])
            threading.Timer(1, lambda: self.config.context.on_continue() if mplayer.is_finished() else False ).start()



