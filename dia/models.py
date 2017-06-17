# -*- coding: utf-8 -*-

from datetime import datetime
import pytz

class Context(object):
    """
    This is the main object that can be used to situate every query
    in a date and time point for a single user.
    
    This also is part of the rest of the models.
    """
    def __init__(self, user_pk, utc_timestamp, tzinfo=pytz.utc):
        self._u = user_pk
        self._ts = utc_timestamp
        self._tz = tzinfo

    @property
    def user_pk(self):
        return self._u
    
    @property
    def utc_timestamp(self):
        return self._ts
    
    @property
    def tzinfo(self):
        return self._tz
    
    @property
    def utc_datetime(self):
        return datetime.fromtimestamp(self._ts, pytz.utc)
    
    @property
    def local_datetime(self):
        return self.utc_datetime.astimezone(self._tz)
    
    def __iter__(self):
        " With this, only with a dict(obj) the object is automatically converted as a dict. "
        yield 'user_pk', self.user_pk
        yield 'utc_timestamp', self.utc_timestamp
        yield 'tzinfo', str(self.tzinfo)
    
    def __str__(self):
        return '{}: {}'.format(type(self).__name__, dict(self))



########################################################################

from abc import ABCMeta

"""
Base abstract class to identificate all the app models as the same in some circumstances 
"""
class DescriptiveModel:
    __metaclass__ = ABCMeta


""""""
class Trait(DescriptiveModel):
    pk            = None
    context       = None
    kind          = None
    value         = None
    def __init__(self, pk=None, context=None, kind=None, value=None):
        self.pk      = pk
        self.context = context
        self.kind    = kind
        self.value   = value
    def __iter__(self):
        """
        With this, only with a dict(obj) the object is automatically
        converted as a dict. Easy then to convert to json.
        And from a dict, we can instantiate models as Model(**dict)
        """
        yield 'pk', self.pk
        yield 'context', dict(self.context)
        yield 'kind', self.kind
        yield 'value', self.value
    def __str__(self):
        return '{}: {}'.format(type(self).__name__, dict(self))
    

""""""
class GlucoseLevel(DescriptiveModel):
    pk        = None
    context   = None
    mgdl_level= None
    
    def __init__(self, pk=None, context=None, mgdl_level=None):
        self.pk            = pk
        self.context = context
        self.mgdl_level    = mgdl_level
    
    def __iter__(self):
        " With this, only with a dict(obj) the object is automatically converted as a dict. "
        yield 'pk', self.pk
        yield 'context', dict(self.context)
        yield 'mgdl_level', self.mgdl_level
    
    def __str__(self):
        return '{}: {}'.format(type(self).__name__, dict(self))


""""""
class Activity(DescriptiveModel):
    pk            = None
    context       = None
    intensity     = None
    minutes       = None
    
    def __init__(self, pk=None, context=None, intensity=None, minutes=None):
        self.pk        = pk
        self.context   = context
        self.intensity = intensity
        self.minutes   = minutes
    
    def __iter__(self):
        " With this, only with a dict(obj) the object is automatically converted as a dict. "
        yield 'pk', self.pk
        yield 'context', dict(self.context)
        yield 'intensity', self.intensity
        yield 'minutes', self.minutes
    
    def __str__(self):
        return '{}: {}'.format(type(self).__name__, dict(self))


""""""
class InsulinAdministration(DescriptiveModel):
    pk            = None
    context       = None
    insulin_type  = None
    insulin_units = None
    
    def __init__(self, pk=None, context=None, insulin_type=None, insulin_units=None):
        self.pk            = pk
        self.context       = context
        self.insulin_type  = insulin_type
        self.insulin_units = insulin_units
    
    def __iter__(self):
        " With this, only with a dict(obj) the object is automatically converted as a dict. "
        yield 'pk', self.pk
        yield 'context', dict(self.context)
        yield 'insulin_type', self.insulin_type
        yield 'insulin_units', self.insulin_units
    
    def __str__(self):
        return '{}: {}'.format(type(self).__name__, dict(self))


""""""
class Feeding(DescriptiveModel):
    pk            = None
    context       = None
    utc_timestamp = None
    total_gr      = None
    total_ml      = None
    carb_gr       = None
    protein_gr    = None
    fat_gr        = None
    fiber_gr      = None
    alcohol_gr    = None
    
    def __init__(self, pk=None, context=None, total_gr=0, total_ml=0, carb_gr=0, protein_gr=0, fat_gr=0, fiber_gr=0, alcohol_gr=0):
        self.pk            = pk
        self.context       = context
        self.total_gr      = total_gr
        self.total_ml      = total_ml
        self.carb_gr       = carb_gr
        self.protein_gr    = protein_gr
        self.fat_gr        = fat_gr
        self.fiber_gr      = fiber_gr
        self.alcohol_gr    = alcohol_gr
    
    def __iter__(self):
        " With this, only with a dict(obj) the object is automatically converted as a dict. "
        yield 'pk', self.pk
        yield 'context', dict(self.context)
        yield 'total_gr', self.total_gr
        yield 'total_ml', self.total_ml
        yield 'carb_gr', self.carb_gr
        yield 'protein_gr', self.protein_gr
        yield 'fat_gr', self.fat_gr
        yield 'fiber_gr', self.fiber_gr
        yield 'alcohol_gr', self.alcohol_gr
    
    def __str__(self):
        return '{}: {}'.format(type(self).__name__, dict(self))



"""
Just enumerations
"""
class TraitKindSexValue:
    MALE   = 'male'
    FEMALE = 'female'

    __metaclass__ = ABCMeta
    

class TraitKind:
    BIRTH_UTC_TIMESTAMP  = 1 # value accepted is long
    HEIGHT_CM            = 2 # value accepted is int
    WEIGHT_KG            = 3 # value accepted is float
    NECK_PERIMETER_CM    = 4 # value accepted is int
    ABDOMEN_PERIMETER_CM = 5 # value accepted is int
    WAIST_PERIMETER_CM   = 6 # value accepted is int
    SEX                  = 7 # one of TraitKindSexValue

    __metaclass__ = ABCMeta


class ActivityIntensity:
    SOFT    = 1 # walking softly
    MEDIUM  = 2 # walking hard, exercise
    HIGH    = 3 # running, softly, weightlifting soft
    EXTREME = 4 # sprints, HIIT, weightlifting hard

    __metaclass__ = ABCMeta


class InsulinType:
    RAPID        = 0
    SHORT        = 1
    INTERMEDIATE = 2
    SLOW         = 3
    ULTRA_SLOW   = 4

    __metaclass__ = ABCMeta
    

