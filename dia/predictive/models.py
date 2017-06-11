


class Context():
    def __init__(self, user_pk, utc_timestamp):
        self._user_pk = user_pk
        self._utc_timestamp = utc_timestamp

    @property
    def user_pk(self):
        return self._user_pk

    @property
    def utc_timestamp(self):
        return self._utc_timestamp


class Recommendation():
    pass
