"""

!!!!!!!!!!!!!!!!!!!   NOT FULLY TESTED !!!!!!!!!!!!!!!!!!!!!!!
!!!!!! MAY NO  BE NEEDED AS datetime.datetime.now() APPEARS TO BE TIMEZONE AWARE NATURALLY !!!!!!!!!!!


Python job scheduling for humans.

An in-process scheduler for periodic jobs that uses the builder pattern
for configuration. Schedule lets you run Python functions (or any other
callable) periodically at pre-determined intervals using a simple,
human-friendly syntax.

Inspired by Addam Wiggins' article "Rethinking Cron" [1] and the
"clockwork" Ruby module [2][3].

Features:
    - A simple to use API for scheduling jobs.
    - Very lightweight and no external dependencies.
    - Excellent test coverage.
    - Works with Python 2.7 and 3.3

Usage:
    >>> import schedule
    >>> import time

    >>> def job(message='stuff'):
    >>>     print("I'm working on:", message)

    >>> schedule.every(10).minutes.do(job)
    >>> schedule.every().hour.do(job, message='things')
    >>> schedule.every().day.at("10:30").do(job)

    >>> while True:
    >>>     schedule.run_pending()
    >>>     time.sleep(1)

[1] http://adam.heroku.com/past/2010/4/13/rethinking_cron/
[2] https://github.com/tomykaira/clockwork
[3] http://adam.heroku.com/past/2010/6/30/replace_cron_with_clockwork/
"""
import datetime
import random
import re

import schedule
from dateutil import parser
from dateutil.tz import tzlocal

from tz import tz_offsets


class TimezoneAwareScheduler(schedule.Scheduler):
    def every(self, interval=1):
        """
        Schedule a new periodic job.

        :param interval: A quantity of a certain time unit
        :return: An unconfigured :class:`Job <Job>`
        """
        job = TimezoneAwareJob(interval, self)
        return job

    @property
    def idle_seconds(self):
        """Number of seconds until `next_run`."""
        return (self.next_run - datetime.datetime.now(tzlocal())
                ).total_seconds()


class TimezoneAwareJob(schedule.Job):
    """A periodic job as used by `Scheduler`."""

    def at(self, time_str):
        """Schedule the job every day at a specific time.

        Calling this is only valid for jobs scheduled to run every
        N day(s).
        """
        if (self.unit not in ('days', 'hours', 'minutes')
                and not self.start_day):
            raise schedule.ScheduleValueError('Invalid unit')
        if not isinstance(time_str, str):
            raise TypeError('at() should be passed a string')
        if self.unit == 'days' or self.start_day:
            if not re.match(r'^([0-2]\d:)?[0-5]\d:[0-5]\d$', time_str):
                raise schedule.ScheduleValueError('Invalid time format')
        if self.unit == 'hours':
            if not re.match(r'^([0-5]\d)?:[0-5]\d$', time_str):
                raise schedule.ScheduleValueError(('Invalid time format for'
                                          ' an hourly job'))
        if self.unit == 'minutes':
            if not re.match(r'^:[0-5]\d$', time_str):
                raise schedule.ScheduleValueError(('Invalid time format for'
                                          ' a minutely job'))
        time_values = time_str.split(':')
        if len(time_values) == 3:
            hour, minute, second = time_values
        elif len(time_values) == 2 and self.unit == 'minutes':
            hour = 0
            minute = 0
            _, second = time_values
        else:
            hour, minute = time_values
            second = 0
        if self.unit == 'days' or self.start_day:
            hour = int(hour)
            if not (0 <= hour <= 23):
                raise schedule.ScheduleValueError('Invalid number of hours')
        elif self.unit == 'hours':
            hour = 0
        elif self.unit == 'minutes':
            hour = 0
            minute = 0
        minute = int(minute)
        second = int(second)
        #self.at_time = datetime.time(hour, minute, second)
        self.at_time = parser.parse("{}:{}:{}".format(hour, minute,second), tzinfos=tz_offsets)
        if not self.at_time.tzinfo:
            self.at_time = self.at_time.replace(tzinfo=tzlocal())
        return self

        # @note this is the modified version
        # assert self.unit == 'days'
        # self.at_time = parser.parse(time_str, tzinfos=tz_offsets)
        # if not self.at_time.tzinfo:
        #     self.at_time = self.at_time.replace(tzinfo=tzlocal())
        # return self

    @property
    def should_run(self):
        """True if the job should be run now."""
        return datetime.datetime.now(tzlocal()) >= self.next_run

    def run(self):
        """Run the job and immediately reschedule it."""
        schedule.logger.info('Running job %s', self)
        ret = self.job_func()
        self.last_run = datetime.datetime.now(tzlocal())
        self._schedule_next_run()
        return ret

    def _schedule_next_run(self):
        """Compute the instant when this job should run next."""
        # Allow *, ** magic temporarily:
        # pylint: disable=W0142
        # assert self.unit in ('seconds', 'minutes', 'hours', 'days', 'weeks')
        # self.period = datetime.timedelta(**{self.unit: self.interval})
        # self.next_run = datetime.datetime.now(tzlocal()) + self.period
        # if self.at_time:
        #     assert self.unit == 'days'
        #     self.next_run = self.next_run.replace(hour=self.at_time.hour,
        #                                           minute=self.at_time.minute,
        #                                           second=self.at_time.second,
        #                                           microsecond=0,
        #                                           tzinfo=self.at_time.tzinfo)
        #     # If we are running for the first time, make sure we run
        #     # at the specified time *today* as well
        #     if (not self.last_run and
        #             self.at_time > datetime.datetime.now(tzlocal())):
        #         self.next_run = self.next_run - datetime.timedelta(days=1)

        """
        Compute the instant when this job should run next.
        """
        if self.unit not in ('seconds', 'minutes', 'hours', 'days', 'weeks'):
            raise schedule.ScheduleValueError('Invalid unit')

        if self.latest is not None:
            if not (self.latest >= self.interval):
                raise schedule.ScheduleError('`latest` is greater than `interval`')
            interval = random.randint(self.interval, self.latest)
        else:
            interval = self.interval

        self.period = datetime.timedelta(**{self.unit: interval})
        self.next_run = datetime.datetime.now(tzlocal()) + self.period
        if self.start_day is not None:
            if self.unit != 'weeks':
                raise schedule.ScheduleValueError('`unit` should be \'weeks\'')
            weekdays = (
                'monday',
                'tuesday',
                'wednesday',
                'thursday',
                'friday',
                'saturday',
                'sunday'
            )
            if self.start_day not in weekdays:
                raise schedule.ScheduleValueError('Invalid start day')
            weekday = weekdays.index(self.start_day)
            days_ahead = weekday - self.next_run.weekday()
            if days_ahead <= 0:  # Target day already happened this week
                days_ahead += 7
            self.next_run += datetime.timedelta(days_ahead) - self.period
        if self.at_time is not None:
            if (self.unit not in ('days', 'hours', 'minutes')
                    and self.start_day is None):
                raise schedule.ScheduleValueError(('Invalid unit without'
                                          ' specifying start day'))
            kwargs = {
                'second': self.at_time.second,
                'microsecond': 0,
                'tzinfo':self.at_time.tzinfo
            }
            if self.unit == 'days' or self.start_day is not None:
                kwargs['hour'] = self.at_time.hour
            if self.unit in ['days', 'hours'] or self.start_day is not None:
                kwargs['minute'] = self.at_time.minute
            self.next_run = self.next_run.replace(**kwargs)
            # If we are running for the first time, make sure we run
            # at the specified time *today* (or *this hour*) as well
            if not self.last_run:
                now = datetime.datetime.now(tzlocal())
                if (self.unit == 'days' and self.at_time.time() > now.time() and
                        self.interval == 1):
                    self.next_run = self.next_run - datetime.timedelta(days=1)
                elif self.unit == 'hours' \
                        and self.at_time.minute > now.minute \
                        or (self.at_time.minute == now.minute
                            and self.at_time.second > now.second):
                    self.next_run = self.next_run - datetime.timedelta(hours=1)
                elif self.unit == 'minutes' \
                        and self.at_time.second > now.second:
                    self.next_run = self.next_run - \
                                    datetime.timedelta(minutes=1)
        if self.start_day is not None and self.at_time is not None:
            # Let's see if we will still make that time we specified today
            if (self.next_run - datetime.datetime.now(tzlocal())).days >= 7:
                self.next_run -= self.period



# The following methods are shortcuts for not having to
# create a Scheduler instance:

#: Default :class:`Scheduler <Scheduler>` object
default_scheduler = TimezoneAwareScheduler()

#: Default :class:`Jobs <Job>` list
jobs = default_scheduler.jobs  # todo: should this be a copy, e.g. jobs()?


def every(interval=1):
    """Calls :meth:`every <Scheduler.every>` on the
    :data:`default scheduler instance <default_scheduler>`.
    """
    return default_scheduler.every(interval)


def run_pending():
    """Calls :meth:`run_pending <Scheduler.run_pending>` on the
    :data:`default scheduler instance <default_scheduler>`.
    """
    default_scheduler.run_pending()


def run_all(delay_seconds=0):
    """Calls :meth:`run_all <Scheduler.run_all>` on the
    :data:`default scheduler instance <default_scheduler>`.
    """
    default_scheduler.run_all(delay_seconds=delay_seconds)


def clear(tag=None):
    """Calls :meth:`clear <Scheduler.clear>` on the
    :data:`default scheduler instance <default_scheduler>`.
    """
    default_scheduler.clear(tag)


def cancel_job(job):
    """Calls :meth:`cancel_job <Scheduler.cancel_job>` on the
    :data:`default scheduler instance <default_scheduler>`.
    """
    default_scheduler.cancel_job(job)


def next_run():
    """Calls :meth:`next_run <Scheduler.next_run>` on the
    :data:`default scheduler instance <default_scheduler>`.
    """
    return default_scheduler.next_run


def idle_seconds():
    """Calls :meth:`idle_seconds <Scheduler.idle_seconds>` on the
    :data:`default scheduler instance <default_scheduler>`.
    """
    return default_scheduler.idle_seconds
