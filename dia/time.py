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
class Instant(object):
    def __init__(self, timestamp=None, dtime=None, timezone=None):
        if timestamp:
            self._timestamp = timestamp
            self._tz = pytz.utc
        elif dtime:
            self._timestamp = calendar.timegm(dtime.astimezone(pytz.utc).utctimetuple())
            if dtime.tzinfo:
                self._tz = dtime.tzinfo
            else:
                self._tz = pytz.utc
        else:
            self._tz = pytz.utc
            self._timestamp = calendar.timegm(pytz.utc.localize(datetime.utcnow()).utctimetuple())
        if timezone:
            self.tz = timezone
    def __str__(self):
        return __name__ + ": timestamp: {}, timezone: {}, datetime: {}".format(self.ts, self.tz, self.dt)
    @property
    def ts(self):
        return self._timestamp
    @property
    def dt(self):
        return datetime.utcfromtimestamp(self.ts).\
            replace(tzinfo=pytz.utc).\
            astimezone(pytz.timezone(self.tz))
    @property
    def tz(self):
        return str(self._tz)
    @tz.setter
    def tz(self, new_tz):
        assert isinstance(new_tz, str) or isinstance(new_tz, unicode)
        try:
            self._tz = pytz.timezone(new_tz)
        except pytz.exceptions.UnknownTimeZoneError:
            raise

    

