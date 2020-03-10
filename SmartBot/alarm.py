import schedule
import time
import re
from datetime import datetime

class Alarm:
    """Alarm class to handle scheduling tasks"""

    def __init__(self, config_object):
        self.config_object = config_object

    def schedule(self):
        if "alarms" in self.config_object.json:
            for alarm in self.config_object.json["alarms"]:
                at = alarm["when"]
                if at is not list:
                    at = [ at ]
                action = alarm["action"]
                args = alarm["args"]
                self.schedule_task(at, action, args)

    def schedule_task(self, at_list, action, args):
        days = []
        time_of_day = None
        time_pattern = re.compile("\d{1,2}:\d\d")

        for at_item in at_list:
            if time_pattern.match(at_item):
                time_of_day = at_item
            else:
                if at_item == "weekday":
                    days = [1,2,3,4,5]
                elif at_item == "weekend":
                    days = [6,0]

        if time_of_day is not None:
            for day in days:
                if day == 0:
                    schedule.every().sunday.at(time_of_day).do(lambda: self.wakeup(action, args))
                elif day == 1:
                    schedule.every().monday.at(time_of_day).do(lambda: self.wakeup(action, args))
                elif day == 2:
                    schedule.every().monday.at(time_of_day).do(lambda: self.wakeup(action, args))
                elif day == 3:
                    schedule.every().monday.at(time_of_day).do(lambda: self.wakeup(action, args))
                elif day == 4:
                    schedule.every().monday.at(time_of_day).do(lambda: self.wakeup(action, args))
                elif day == 5:
                    schedule.every().monday.at(time_of_day).do(lambda: self.wakeup(action, args))
                elif day == 6:
                    schedule.every().monday.at(time_of_day).do(lambda: self.wakeup(action, args))

    def wakeup(self, action, args):
        now = datetime.now()
        date_time = now.strftime("%Y-%m-%d %H:%M:%S")
        print("[ALARM] Woke at ", date_time, " to ", action, " ", str(args))


