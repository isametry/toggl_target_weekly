#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @author Mosab Ibrahim <mosab.a.ibrahim@gmail.com>

import os
import sys
import requests

from urllib.parse import urlencode
from requests.auth import HTTPBasicAuth
from dateutil.rrule import rrule, DAILY, SA, SU, MO, TU, WE, TH, FR
from dateutil.relativedelta import relativedelta, MO, SU
from datetime import datetime

# Toggl API Token
API_TOKEN = 'b356550913a832f0a1fa0c22f9d995e3'

# Target Configurations
WORKING_HOURS_GOAL = 7

# Timezone
TIMEZONE = '+02:00'

# Week Days
WEEK_DAYS = (MO, TU, WE, TH, FR, SA, SU)

def main():
    w = WorkingTime(WORKING_HOURS_GOAL, WEEK_DAYS)
    a = TogglAPI(API_TOKEN, TIMEZONE)
    t = Target()

    if not internet_on():
        print("No internet connection!")
        sys.exit()
    try:
        t.achieved_hours = a.get_hours_tracked(start_date=w.period_start, end_date=w.now)
    except:
        print("Toggle request failed!")
        sys.exit()

    t.required_hours = w.required_hours_this_period

    print("\nThis week's target:")
    print(hilite("{0:.2f} hours".format(w.required_hours_this_period), None, True))

    goal_complete = (w.required_hours_this_period <= t.achieved_hours)

    print("\nDone so far:")
    print(hilite("{0:.2f} hours".format(t.achieved_hours), goal_complete, True))

    if goal_complete:
        print("\nGoal is complete!\nExceeded by:")
        print(hilite("{0:.2f} hours".format(- w.required_hours_this_period + t.achieved_hours), goal_complete, True))
    else:
        print("\nRemains:")
        print(hilite("{0:.2f} hours".format(w.required_hours_this_period - t.achieved_hours), goal_complete, True))

        print("\nHow your progress looks:")
        bar = percentile_bar(t.achieved_percentage)
        print(bar)

def internet_on():
    """Checks if internet connection is on by connecting to Google"""
    try:
        requests.get('http://www.google.com', timeout=10)
        return True
    except requests.exceptions.ConnectionError:
        return False
    except:
        return False


def getTerminalSize():
    env = os.environ

    def ioctl_GWINSZ(fd):
        try:
            import fcntl
            import termios
            import struct
            cr = struct.unpack('hh', fcntl.ioctl(fd, termios.TIOCGWINSZ, '1234'))
        except:
            return
        return cr

    cr = ioctl_GWINSZ(0) or ioctl_GWINSZ(1) or ioctl_GWINSZ(2)

    if not cr:
        try:
            fd = os.open(os.ctermid(), os.O_RDONLY)
            cr = ioctl_GWINSZ(fd)
            os.close(fd)
        except:
            pass
    if not cr:
        cr = (env.get('LINES', 25), env.get('COLUMNS', 80))

    return int(cr[1]), int(cr[0])


def percentile_bar(percentage):
    (width, height) = getTerminalSize()

    progress_units = width - 10
    achieved_units = int(percentage * progress_units)
    remaining_units = int(progress_units - achieved_units)

    progress_bar = "{}{}".format("=" * achieved_units, "-" * remaining_units)

    percentile_bar = "{0:.2f}% ".format(percentage * 100)
    percentile_bar += "[{}]".format(progress_bar)

    return percentile_bar


def hilite(string, status, bold):
    attr = []
    if status:
        # green
        attr.append('32')
    if not status:
        # red
        attr.append('31')
    if status == None:
        attr.append('34')
    if bold:
        attr.append('1')
    return '\x1b[%sm%s\x1b[0m' % (';'.join(attr), string)
class WorkingTime(object):
    """Time and date calculations for working hours and days"""

    def __init__(self, hour_goal, WEEK_DAYS):
        self.goal_hours = hour_goal
        self.WEEK_DAYS = WEEK_DAYS

    @property
    def now(self):
        return datetime.now() + relativedelta(microsecond=0)

    @property
    def period_start(self):
        return self.now + relativedelta(hour=0, minute=0, second=0, microsecond=0, weekday=MO)

    @property
    def period_end(self):
        return self.now + relativedelta(hour=11, minute=59, second=59, microsecond=0, weekday=SU)

    @property
    def total_days_count(self):
        return rrule(DAILY, dtstart=self.period_start, until=self.period_end, byweekday=self.WEEK_DAYS).count()

    @property
    def days_left_count(self):
        return rrule(DAILY, dtstart=self.now, until=self.period_end, byweekday=self.WEEK_DAYS).count()

    @property
    def days_elapsed_count(self):
        firstday = self.period_start
        today = self.now
        return rrule(DAILY, dtstart=firstday, until=today, byweekday=self.WEEK_DAYS).count()

    @property
    def required_hours_this_period(self):
        return self.goal_hours


class Target(object):
    """Calculate the actual target achievments"""

    def __init__(self):
        super(Target, self).__init__()

    @property
    def minimum_hours(self):
        return self.required_hours

    @property
    def left_to_required(self):
        m = self.required_hours - self.achieved_hours
        return max(m, 0)

    @property
    def achieved_percentage(self):
        return self.achieved_hours / self.required_hours

    def get_required_daily_hours(self, days):
        required_hours = self.left_to_required / max(days, 1)
        return (required_hours)


class TogglAPI(object):
    """A wrapper for Toggl Api"""

    def __init__(self, api_token, timezone):
        self.api_token = api_token
        self.timezone = timezone

    def _make_url(self, section='time_entries', params={}):

        url = 'https://api.track.toggl.com/api/v8/{}'.format(section)
        if len(params) > 0:
            url = url + '?{}'.format(urlencode(params))
        return url

    def _query(self, url, method):
        """Performs the actual call to Toggl API"""

        url = url
        headers = {'content-type': 'application/json'}

        if method == 'GET':
            return requests.get(url, headers=headers, auth=HTTPBasicAuth(self.api_token, 'api_token'))
        elif method == 'POST':
            return requests.post(url, headers=headers, auth=HTTPBasicAuth(self.api_token, 'api_token'))
        else:
            raise ValueError('Undefined HTTP method "{}"'.format(method))

    # Time Entry functions
    def get_time_entries(self, start_date='', end_date='', timezone=''):
        """Get Time Entries JSON object from Toggl within a given start_date and an end_date with a given timezone"""

        url = self._make_url(section='time_entries',
                             params={'start_date': start_date + self.timezone, 'end_date': end_date + self.timezone})
        r = self._query(url=url, method='GET')
        return r.json()

    def get_hours_tracked(self, start_date, end_date):
        """Count the total tracked hours within a given start_date and an end_date
        excluding any RUNNING real time tracked time entries
        """
        time_entries = self.get_time_entries(start_date=start_date.isoformat(), end_date=end_date.isoformat())

        if time_entries is None:
            return 0

        total_seconds_tracked = sum(max(entry['duration'], 0) for entry in time_entries)

        return (total_seconds_tracked / 60.0) / 60.0


if __name__ == '__main__':
    main()
