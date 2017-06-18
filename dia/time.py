# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
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
    
    #############################################################
    def __add__(self, other):
        assert isinstance(other, timedelta), "add operation only supported with timedelta objects"
        return Instant(timestamp=(other.total_seconds() + self.ts), timezone=self.tz)
    
    def __radd__(self, other):
        return self.__add__(other)
    
    def __sub__(self, other):
        assert isinstance(other, timedelta) or isinstance(other, Instant) or isinstance(other, datetime), "subtract operation only supported with timedelta, datetime or Instant objects"
        if isinstance(other, timedelta):
            return Instant(timestamp=(self.ts - other.total_seconds()), timezone=self.tz)
        if isinstance(other, datetime):
            assert other.tzinfo, "naive datetimes is not supported"
            current_ts = self.ts
            other_ts = Instant(dtime=other).ts
            seconds = current_ts - other_ts
            return timedelta(seconds=seconds)
        if isinstance(other, Instant):
            current_ts = self.ts
            other_ts = other.ts
            seconds = current_ts - other_ts
            return timedelta(seconds=seconds)
    
    def __rsub__(self, other):
        return self.__sub__(other)

    def __str__(self):
        return __name__ + ": timestamp: {}, timezone: {}, datetime: {}".format(self.ts, self.tz, self.dt)
    

