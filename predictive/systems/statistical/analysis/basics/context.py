# -*- coding: utf-8 -*-
from ...tools.dates import Datetime


class Context(object):

    def __init__(self, user_id, current_datetime):
        assert isinstance(current_datetime, Datetime), "es necesario que current_datetime sea una instancia Datetime válida"
        self._user_id = user_id
        self._current_datetime = current_datetime

    def __str__(self):
        st = "Context: user_id: {}, current_datetime: {}".format(self.user_id, self.current_datetime)
        return st
    
    @property
    def user_id(self):
        return self._user_id
    
    @property
    def current_datetime(self):
        return self._current_datetime

