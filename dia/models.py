# -*- coding: utf-8 -*-


########################################################################

from abc import ABCMeta

"""
Base abstract class to identificate all the app models as the same, in some circumstances 
"""
class DescriptiveModel:
    # __metaclass__ = ABCMeta
    pass


""""""
class Trait(DescriptiveModel):
    pk            = None
    user_pk       = None
    utc_timestamp = None
    kind          = None
    value         = None
    def __init__(self, pk=None, user_pk=None, utc_timestamp=None, kind=None, value=None):
        self.pk            = pk
        self.user_pk       = user_pk
        self.utc_timestamp = utc_timestamp
        self.kind          = kind
        self.value         = value
    def __iter__(self):
        """
        With this, only with a dict(obj) the object is automatically
        converted as a dict. Easy then to convert to json.
        And from a dict, we can instantiate models as Model(**dict)
        """
        yield 'pk', self.pk
        yield 'user_pk', self.user_pk
        yield 'utc_timestamp', self.utc_timestamp
        yield 'kind', self.kind
        yield 'value', self.value
    def __str__(self):
        return '{}: {}'.format(type(self).__name__, dict(self))
    

""""""
class GlucoseLevel(DescriptiveModel):
    pk            = None
    user_pk       = None
    utc_timestamp = None
    mgdl_level    = None
    
    def __init__(self, pk=None, user_pk=None, utc_timestamp=None, mgdl_level=None):
        self.pk            = pk
        self.user_pk       = user_pk
        self.utc_timestamp = utc_timestamp
        self.mgdl_level    = mgdl_level
    
    def __iter__(self):
        " With this, only with a dict(obj) the object is automatically converted as a dict. "
        yield 'pk', self.pk
        yield 'user_pk', self.user_pk
        yield 'utc_timestamp', self.utc_timestamp
        yield 'mgdl_level', self.mgdl_level
    
    def __str__(self):
        return '{}: {}'.format(type(self).__name__, dict(self))


""""""
class Activity(DescriptiveModel):
    pk            = None
    user_pk       = None
    utc_timestamp = None
    intensity     = None
    minutes       = None
    
    def __init__(self, pk=None, user_pk=None, utc_timestamp=None, intensity=None, minutes=None):
        self.pk            = pk
        self.user_pk       = user_pk
        self.utc_timestamp = utc_timestamp
        self.intensity     = intensity
        self.minutes       = minutes
    
    def __iter__(self):
        " With this, only with a dict(obj) the object is automatically converted as a dict. "
        yield 'pk', self.pk
        yield 'user_pk', self.user_pk
        yield 'utc_timestamp', self.utc_timestamp
        yield 'intensity', self.intensity
        yield 'minutes', self.minutes
    
    def __str__(self):
        return '{}: {}'.format(type(self).__name__, dict(self))


""""""
class InsulinAdministration(DescriptiveModel):
    pk            = None
    user_pk       = None
    utc_timestamp = None
    insulin_type  = None
    insulin_units = None
    
    def __init__(self, pk=None, user_pk=None, utc_timestamp=None, insulin_type=None, insulin_units=None):
        self.pk            = pk
        self.user_pk       = user_pk
        self.utc_timestamp = utc_timestamp
        self.insulin_type  = insulin_type
        self.insulin_units = insulin_units
    
    def __iter__(self):
        " With this, only with a dict(obj) the object is automatically converted as a dict. "
        yield 'pk', self.pk
        yield 'user_pk', self.user_pk
        yield 'utc_timestamp', self.utc_timestamp
        yield 'insulin_type', self.insulin_type
        yield 'insulin_units', self.insulin_units
    
    def __str__(self):
        return '{}: {}'.format(type(self).__name__, dict(self))


""""""
class Feeding(DescriptiveModel):
    pk            = None
    user_pk       = None
    utc_timestamp = None
    total_gr      = None
    total_ml      = None
    carb_gr       = None
    protein_gr    = None
    fat_gr        = None
    fiber_gr      = None
    alcohol_gr    = None
    
    def __init__(self, pk=None, user_pk=None, utc_timestamp=None, total_gr=0, total_ml=0, carb_gr=0, protein_gr=0, fat_gr=0, fiber_gr=0, alcohol_gr=0):
        self.pk            = pk
        self.user_pk       = user_pk
        self.utc_timestamp = utc_timestamp
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
        yield 'user_pk', self.user_pk
        yield 'utc_timestamp', self.utc_timestamp
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
    

