import logging
import threading
import schedule
import re
import queue
from datetime import datetime
import threading
from alarm_events.alarm_event import AlarmEvent
from alarm_events.alarm_factory import create_alarm_event
from event import Event, EventEnum
from states.alarm_state import AlarmState


class Alarm:
    """Alarm class to handle scheduling tasks"""

    def __init__(self, config_object):
        self.config_object = config_object
        self._alarm_config = []
        if "alarms" in self.config_object.json:
            self._alarm_config = self.config_object.json["alarms"]
        self._running = False
        self._schedule()

    def is_running(self):
        return self._running

    def start(self):
        if self._running is False:
            self._running = True
            if schedule.next_run() is None:
                logging.info("no jobs to run")
                self.stop()
            else:
                self._timer()

    def stop(self):
        if self._running:
            self._running = False
            logging.debug("Stopping alarm")

    def update_schedule(self, alarm_config):
        self.stop()
        schedule.clear() # clear all jobs immediately
        self._alarm_config = alarm_config
        self._schedule()

    def _schedule(self):
        """this is the main call to scheduler"""
        schedule.clear() # clears all jobs
        # schedule.every(1).minutes.do(lambda: self.wakeup("test", None))
        if len(self._alarm_config) > 0:
            for alarm in self._alarm_config:
                at = alarm["when"]
                if type(at) is not list:
                    at = [at]
                action = alarm["action"]
                args = alarm["args"]
                alarm_event = create_alarm_event(action, args, self.config_object)
                alarm_event.validate()  # will throw exception if not correct
                self._schedule_task(at, alarm_event)
                schedule.run_pending()
                logging.info("Next job to run at {}".format(schedule.next_run()))

    def _timer(self):
        """This is the callback function which is run each second"""
        if self._running:
            #logging.debug("{} Schedule wokeup, next job is {}".format(datetime.now(), schedule.next_run()))
            schedule.run_pending()
            if schedule.next_run() is None:
                logging.info("no jobs to run, stopping scheduler")
                self.stop()
            threading.Timer(1, self._timer).start()

    def _schedule_task(self, at_list, alarm_event: AlarmEvent):
        """do the actual scheduling of a task"""
        days = []
        time_of_day = None
        time_pattern = re.compile("\d{1,2}:\d\d")

        for at_item in at_list:
            if time_pattern.match(at_item):
                time_of_day = at_item
            else:
                if at_item == "weekdays":
                    days = [1, 2, 3, 4, 5]
                elif at_item == "weekend":
                    days = [6, 0]
                elif at_item == "monday":
                    days = [1]
                elif at_item == "tuesday":
                    days = [2]
                elif at_item == "wednesday":
                    days = [3]
                elif at_item == "thursday":
                    days = [4]
                elif at_item == "friday":
                    days = [5]
                elif at_item == "saturday":
                    days = [6]
                elif at_item == "sunday":
                    days = [0]

        if len(days) == 0:
            # if no days specified we assume we just have a time and set it today
            # only really used in debugging
            # Python weekday is not the same as cron
            # Monday = 0 in Python, while in cron its Sunday
            python_weekday = datetime.today().weekday()
            if python_weekday == 6:
                cron_weekday = 0
            else:
                cron_weekday = python_weekday + 1
            days.append(cron_weekday)

        logging.info("Setting alarm for days {} at {} for {}".format(days, time_of_day, str(alarm_event)))


        if time_of_day is not None:
            for day in days:
                if day == 0:
                    schedule.every().sunday.at(time_of_day).do(self._wakeup,alarm_event)
                elif day == 1:
                    schedule.every().monday.at(time_of_day).do(self._wakeup,alarm_event)
                elif day == 2:
                    schedule.every().tuesday.at(time_of_day).do(self._wakeup,alarm_event)
                elif day == 3:
                    schedule.every().wednesday.at(time_of_day).do(self._wakeup,alarm_event)
                elif day == 4:
                    schedule.every().thursday.at(time_of_day).do(self._wakeup,alarm_event)
                elif day == 5:
                    schedule.every().friday.at(time_of_day).do(self._wakeup,alarm_event)
                elif day == 6:
                    schedule.every().saturday.at(time_of_day).do(self._wakeup,alarm_event)

    def _wakeup(self, alarm_event: AlarmEvent):
        """
        This function is called when our alarm wakes up, its a callback and issues the alarm event
        with an action.
        If alarm is not running then the function might fire, but the event will not be generated.
        ***** Does wake up in a different thread so we just want to communicate with the main
        loop to dispatch. ****
        """
        logging.debug("woke up in thread {}".format(threading.get_ident()))
        if self._running:
            # send message to main thread to execute alarm state
            now = datetime.now()
            date_time = now.strftime("%Y-%m-%d %H:%M:%S")
            logging.info("Woke at {} to {}".format(date_time, alarm_event))
            ev = Event(EventEnum.INTERRUPT)
            if self.config_object.context is not None:
                ev.target_state = AlarmState(self.config_object, self.config_object.context.personality, alarm_event)
                logging.debug("attempting to add event to context queue")
                self.config_object.context.add_event(ev)
                #logging.debug("do interrupt")
                #self.config_object.context.do_interrupt(ev)
        if "run_once" in alarm_event.data:
            if alarm_event.data["run_once"]:
                logging.debug("Cancelling job as run_once was true")
                return schedule.CancelJob
