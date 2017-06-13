# -*- coding: utf-8 -*-
from ...tools.dates import Datetime


class Context(object):

    def __init__(self, user_pk, utc_timestamp):
        self._user_id = user_pk
        self._current_datetime = Datetime.utcfromtimestamp(utc_timestamp)

    def __str__(self):
        st = "Context: user_pk: {}, current_datetime: {}".format(self.user_pk, self.current_datetime)
        return st
    
    @property
    def user_pk(self):
        return self._user_pk
    
    @property
    def current_datetime(self):
        return self._current_datetime

