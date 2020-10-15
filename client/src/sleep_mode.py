import datetime
from event import EventEnum, Event

class SleepMode:
    """
    Sleep mode is linked to SleepState and handles its management
    The configuration for SleepMode is kept in Personality settings
    """
    def __init__(self,
                 app_state
                 ):
        self.app_state = app_state
        self.json = self.app_state.personality.get_sleep_mode()
        self.check_sleep_spec_is_valid()
        self.hard_sleep_datetime = None
        self.soft_sleep_datetime = None
        self.end_sleep_datetime = None
        self.setup_sleep_timings()

    def has_sleep_mode(self):
        return self.json is not None

    def is_sleep_mode_enabled(self):
        """
        If has a sleep mode then we are enabled by default
        If sleep mode has a 'enabled' key then if this is true then enabled, otherwise its false
        :return:
        """
        if self.has_sleep_mode():
            if "enabled" in self.json:
                return self.json["enabled"] == True
            return True
        return False

    def get_hard_sleep_time(self):
        if self.json is None: return None
        if "begin" in self.json:
            if type(self.json["begin"]) is dict:
                if "hard" in self.json["begin"]:
                    return self.json["begin"]["hard"]
        return None

    def get_soft_sleep_time(self):
        if self.json is None: return None
        if "begin" in self.json:
            if type(self.json["begin"]) is dict:
                if "soft" in self.json["begin"]:
                    return self.json["begin"]["soft"]
        return None

    def get_end_sleep_time(self):
        if self.json is None: return None
        if "end" in self.json:
            return self.json["end"]
        return None

    def get_on_end_sleep_action(self):
        if self.json is None: return None
        if "on_end" in self.json:
            return self.json["on_end"]
        return None

    def check_sleep_spec_is_valid(self):
        if self.is_sleep_mode_enabled():
            if not self.get_hard_sleep_time():
                raise ValueError("No hard sleep value")
            if not self.get_soft_sleep_time():
                raise ValueError("No soft sleep value")
            if not self.get_end_sleep_time():
                raise ValueError("Sleep mode missing end key")
            if not self.get_on_end_sleep_action() :
                raise ValueError("Sleep mode missing on_end key")
        return True

    def get_today_as_string(self):
        when = datetime.datetime.now()
        today_as_string = when.strftime("%Y-%m-%d")
        return today_as_string

    def _get_hard_sleep_as_datetime(self):
        """
        Get the user selected time as a datetime object with todays date.
        :return:
        """
        user_time = self.get_hard_sleep_time()
        if user_time is None: return None
        today_as_string = self.get_today_as_string()
        if self.get_hard_sleep_time():
            sleep_time = datetime.datetime.strptime("{} {}".format(today_as_string, self.get_hard_sleep_time()),
                                                        "%Y-%m-%d %H:%M")
            return sleep_time
        return None

    def _get_soft_sleep_as_datetime(self):
        """
        Get the user selected time as a datetime object with todays date.
        :return:
        """
        user_time = self.get_soft_sleep_time()
        if user_time is None: return None
        today_as_string = self.get_today_as_string()
        if self.get_soft_sleep_time():
            sleep_time = datetime.datetime.strptime("{} {}".format(today_as_string, self.get_soft_sleep_time()),
                                                    "%Y-%m-%d %H:%M")
            return sleep_time
        return None

    def get_earliest_start(self):
        """
        Get the minimum of hard and soft date times with the current date.
        No adjustment is made in this function for the day relative to the current time.
        :return:
        """
        soft = self._get_soft_sleep_as_datetime()
        hard = self._get_hard_sleep_as_datetime()
        if soft is None and hard is None:
            return None
        if soft is None and hard is not None:
            return hard
        if soft is not None and hard is None:
            return soft
        when = min(soft, hard)
        return when

    def get_latest_start(self):
        """
        Get the maximum of hard and soft date times with the current date.
        No adjustment is made in this function for the day relative to the current time.
        :return:
        """
        soft = self._get_soft_sleep_as_datetime()
        hard = self._get_hard_sleep_as_datetime()
        if soft is None and hard is None:
            return None
        if soft is None and hard is not None:
            return hard
        if soft is not None and hard is None:
            return soft
        when = max(soft, hard)
        return when

    def get_end_sleep_as_datetime(self):
        user_time = self.get_end_sleep_time()
        if user_time is None: return None
        today_as_string = self.get_today_as_string()
        end_time = datetime.datetime.strptime("{} {}".format(today_as_string, self.get_end_sleep_time()),
                                          "%Y-%m-%d %H:%M")
        return end_time

    def setup_sleep_timings(self):
        """
        Sets the member attributes with the sleep start and end adjusted for the current time.
        :return:
        """
        if not self.is_sleep_mode_enabled():
            return
        self.end_sleep_datetime = self.get_end_sleep_as_datetime()
        self.soft_sleep_datetime = self.get_earliest_start()
        self.hard_sleep_datetime = self.get_latest_start()
        current_time = datetime.datetime.now()

        if self.end_sleep_datetime < self.soft_sleep_datetime:
            if current_time <= self.end_sleep_datetime:
                self.soft_sleep_datetime = self.soft_sleep_datetime + datetime.timedelta(days=-1)
                self.hard_sleep_datetime = self.hard_sleep_datetime + datetime.timedelta(days=-1)
            else:
                self.end_sleep_datetime = self.end_sleep_datetime + datetime.timedelta(days=1)
        else:
            if current_time <= self.end_sleep_datetime:
                pass
            else:
                # all are next day
                self.end_sleep_datetime = self.end_sleep_datetime + datetime.timedelta(days=1)
                self.soft_sleep_datetime = self.soft_sleep_datetime + datetime.timedelta(days=1)
                self.hard_sleep_datetime = self.hard_sleep_datetime + datetime.timedelta(days=1)

    def create_wake_up_event(self):
        ev = Event(EventEnum.EXIT_SLEEP)
        ev.override_ignorable_events = True
        return ev

    def is_ready_to_wake_up(self):
        """
        Only returns TRUE during the minute that we waking up
        :return:
        """
        if not self.is_sleep_mode_enabled():
            return False
        when = datetime.datetime.now()
        end_time = self.end_sleep_datetime
        if when >= end_time:
            return True
        return False

    def create_soft_sleep_event(self):
        ev = Event(EventEnum.ENTER_SLEEP_IF_ABLE)
        return ev

    def create_hard_sleep_event(self):
        ev = Event(EventEnum.ENTER_SLEEP_NOW)
        return ev

    def is_ready_to_sleep(self):
        """
        Should return TRUE while we are sleeping until the end time is hit
        :return:
        """
        when = datetime.datetime.now()
        if not self.is_sleep_mode_enabled():
            return False
        if when >= self.end_sleep_datetime:
            return False
        if when >= self.hard_sleep_datetime:
            return self.create_hard_sleep_event()
        elif when >= self.soft_sleep_datetime:
            return self.create_soft_sleep_event()
        else:
            return False
