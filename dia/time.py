# -*- coding: utf-8 -*-
from datetime import datetime
import calendar
import pytz

"""
To create aware datetimes, the correct way is as follows:

tz = pytz.timezone('Europe/Madrid')
local_dt = datetime.now()
aware_local_dt = tz.localize(local_dt)

local_dt:
datetime.datetime(2017, 6, 18, 7, 6, 46, 722048)

aware_local_dt:
datetime.datetime(2017, 6, 18, 7, 6, 46, 722048, tzinfo=<DstTzInfo 'Europe/Madrid' CEST+2:00:00 DST>)
"""
class Timestamp(object):
    def __init__(self, arg):
        if isinstance(arg, long) or isinstance(arg, int):
            self._timestamp = arg
            self._tz = pytz.utc
        elif isinstance(arg, datetime):
            self._timestamp = calendar.timegm(arg.astimezone(pytz.utc).utctimetuple())
            if arg.tzinfo:
                self._tz = arg.tzinfo
            else:
                self._tz = pytz.utc
        elif arg == None:
            self._tz = pytz.utc
            self._timestamp = 0
        else:
            raise ValueError("arg is an instance of invalid type")
    def __str__(self):
        return "Timestamp: {}, timezone: {}, datetime: {}".format(self.ts, self.tz, self.dt)
    @property
    def ts(self):
        return self._timestamp
    @property
    def dt(self):
        return datetime.utcfromtimestamp(self.ts).\
            replace(tzinfo=pytz.utc).\
            astimezone(self.tz)
    @property
    def tz(self):
        return self._tz
    @tz.setter
    def tz(self, new_tz):
        assert isinstance(new_tz, str) or isinstance(new_tz, unicode)
        try:
            self._tz = pytz.timezone(new_tz)
        except pytz.exceptions.UnknownTimeZoneError:
            raise

    

