# -*- coding: utf-8 -*-
from datetime import time, datetime, timedelta


class Time(time):
    def __init__(self, hour, minute=0, second=0):
        super(Time, self).__init__(hour, minute, second)
    def __add__(self, other):
        assert isinstance(other, Timedelta) or isinstance(other, timedelta), "operacion suma solo permitida con Timedelta o timedelta"
        dt = datetime.combine(datetime.today(), self) + other
        t = dt.time()
        return Time(t.hour, t.minute, t.second)
    def __radd__(self, other):
        return self.__add__(other)
    def __sub__(self, other):
        assert isinstance(other, Timedelta) or isinstance(other, Time) or isinstance(other, timedelta) or isinstance(other, time), "operacion resta solo permitida con Timedelta, timedelta, Time o time"
        if isinstance(other, Timedelta) or isinstance(other, timedelta):
            dt = datetime.combine(datetime.today(), self) - other
            t = dt.time()
            return Time(t.hour, t.minute, t.second)
        if isinstance(other, Time) or isinstance(other, time):
            self_dt = datetime.combine(datetime.today(), self)
            other_dt = datetime.combine(datetime.today(), other)
            seconds = (self_dt - other_dt).total_seconds()
            return Timedelta(seconds=seconds)
    def __rsub__(self, other):
        return self.__sub__(other)
    @staticmethod
    def minutes2time(minutes):
        return Time(hour=int(minutes / 60), minute=int(minutes % 60))
    @staticmethod
    def time2minutes(time_):
        return (time_.hour * 60) + time_.minute
    def minutes(self):
        return Time.time2minutes(self)


class Datetime(datetime):
    def __init__(self, year, month, day, hour=0, minute=0, second=0):
        super(Datetime, self).__init__(year, month, day, hour, minute, second)
    @staticmethod
    def combine(dt, t):
        return Datetime(dt.year, dt.month, dt.day, t.hour, t.minute, t.second)
    @staticmethod
    def nearest_datetime_static(dt, dt_list):
        nearest_dt = None
        nearest_minutes = None
        for element in dt_list:
            if nearest_dt == None:
                nearest_dt = element
                nearest_minutes = abs((dt - element).total_seconds() / 60.)
                continue
            current_nearest_minutes = abs((dt - element).total_seconds() / 60.)
            if current_nearest_minutes < nearest_minutes:
                nearest_minutes = current_nearest_minutes
                nearest_dt = element
        return nearest_dt
    def nearest_datetime(self, dt_list):
        nearest_dt = None
        nearest_minutes = None
        for element in dt_list:
            if nearest_dt == None:
                nearest_dt = element
                nearest_minutes = abs((self - element).total_seconds() / 60.)
                continue
            current_nearest_minutes = abs((self - element).total_seconds() / 60.)
            if current_nearest_minutes < nearest_minutes:
                nearest_minutes = current_nearest_minutes
                nearest_dt = element
        return nearest_dt
    @staticmethod
    def now():
        dt = datetime.now()
        return Datetime(dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second)
    @staticmethod
    def utcfromtimestamp(timestamp):
        dt = datetime.utcfromtimestamp(timestamp)
        return Datetime(dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second)
    @property
    def seconds_from_epoch(self):
        epoch = Datetime.utcfromtimestamp(0)
        return (self - epoch).total_secs
    """
    para soportar operaciones aritméticas y que se devuelvan Timedeltas nuestros
    """
    def __add__(self, other):
        assert isinstance(other, Timedelta) or isinstance(other, timedelta), "operacion suma solo permitida con Timedelta"
        epoch = datetime.utcfromtimestamp(0)
        current = datetime(self.year, self.month, self.day, self.hour, self.minute, self.second)
        seconds = (current - epoch).total_seconds()
        dt = datetime.utcfromtimestamp(seconds + other.total_seconds())
        return Datetime(dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second)
    def __radd__(self, other):
        return self.__add__(other)
    def __sub__(self, other):
        assert isinstance(other, Timedelta) or isinstance(other, Datetime) or isinstance(other, timedelta) or isinstance(other, datetime), "operacion resta solo permitida con Timedelta, timedelta, Datetime o datetime"
        if isinstance(other, Timedelta) or isinstance(other, timedelta):
            epoch = datetime.utcfromtimestamp(0)
            current = datetime(self.year, self.month, self.day, self.hour, self.minute, self.second)
            seconds = (current - epoch).total_seconds()
            dt = datetime.utcfromtimestamp(seconds - other.total_secs)
            return Datetime(dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second)
        if isinstance(other, Datetime) or isinstance(other, datetime):
            current = datetime(self.year, self.month, self.day, self.hour, self.minute, self.second)
            other = datetime(other.year, other.month, other.day, other.hour, other.minute, other.second)
            seconds = (current - other).total_seconds()
            return Timedelta(seconds=seconds)
    def __rsub__(self, other):
        return self.__sub__(other)
    

class Timedelta(timedelta):
    def __init__(self, *args, **kvargs):
        super(Timedelta, self).__init__(*args, **kvargs)
    @property
    def total_secs(self):
        return int(self.total_seconds())
    @property
    def total_mins(self):
        return int(self.total_seconds() / 60.)
    @property
    def total_hours(self):
        return int(self.total_seconds() / 60. / 60.)
    @property
    def total_days(self):
        return int(self.total_seconds() / 60. / 60. / 24.)
    @property
    def total_years(self):
        return int((self.total_hours / 24.) * 0.00273791)
    
    
    

