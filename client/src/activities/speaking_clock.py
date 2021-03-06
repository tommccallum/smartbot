import datetime
import logging
import time

from activities.continuous_state import ContinuousState


class SpeakingClockState(ContinuousState):
    """
        Announcement interruption to main function

        Usages include making announcements to the user such as errors.

        Example:
        ev = Event(Event.INTERRUPT)
        state = AnnounceState(config, personality)
        state.message = "Something to say"
        ev.target_state = state
        context.do_interrupt(ev)

    """

    def __init__(self,
                 app_state,
                 state_configuration=None
                 ) -> None:
        super().__init__(app_state, state_configuration)
        self.last_date_said = None

    def do_work_in_thread(self, is_first_run):
        when = datetime.datetime.now()
        logging.debug("minute={} last_time={}".format(when.minute, self.last_date_said))
        if self.status == ContinuousState.RESUMING or self.last_date_said is None or when.strftime("%Y-%m-%d %H:%M") != self.last_date_said.strftime("%Y-%m-%d %H:%M"): # dont say the same datetime twice
            if self.status == ContinuousState.RESUMING or when.second < 10 or is_first_run: # ensure we say immediately when first loaded
                logging.debug("time is now: {}".format(when))
                self.tell(when)
                self.last_date_said = when # cache this time
        time.sleep(5)

    def tell(self, when):
        logging.debug(when)
        day_of_week_name = when.strftime("Today is %A, the <DAY><DAYTH> of %B, %Y.")
        n = int(when.day)
        day_of_week_name = day_of_week_name.replace("<DAY>", str(n))
        dayth = "th"
        if n == 1 or n == 21 or n == 31:
            dayth = "st"
        elif n == 2 or n == 22:
            dayth = "nd"
        elif n == 3 or n == 23:
            dayth = "rd"

        day_of_week_name = day_of_week_name.replace("<DAYTH>", dayth)

        if when.hour >= 21:
            postfix = " at night."
        elif when.hour >= 18:
            postfix = " in the evening."
        elif when.hour >= 12:
            postfix = " in the afternoon."
        elif when.hour < 2:
            postfix = " at night"
        elif when.hour < 6:
            postfix = " in the early morning"
        else:
            postfix = " in the morning."

        if when.hour == 0 and when.minute == 0:
            message = "The time is midnight."
        elif when.hour == 12 and when.minute == 0:
            message = "The time is midday."
        else:
            hour = when.hour % 12
            next_hour = (hour + 1) % 12
            if hour == 0:
                hour = 12
                next_hour = 1
            if when.minute == 0:
                message = "The time is {} o'clock".format(hour)
            elif when.minute < 50:
                message = "The time is {} minutes past {}".format(when.minute, hour)
            elif when.minute > 49:
                message = "The time is {} minutes to {}".format(60 - when.minute, next_hour)
            else:
                message = "The time is half past {}".format(when.minute, hour)
            message += postfix

        self.app_state.voice_library.say(day_of_week_name, None, False)
        #time.sleep(2)
        self.app_state.voice_library.say(message, None, False)
