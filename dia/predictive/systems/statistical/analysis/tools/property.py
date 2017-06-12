
def propertycached(fn):
    attr_name = "_cached_" + fn.__name__
    
    @property
    def _propertycached(self):
        if not hasattr(self, attr_name):
            setattr(self, attr_name, fn(self))
        return getattr(self, attr_name)
    return _propertycached
