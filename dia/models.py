from abc import ABCMeta


class DescriptiveModel:
    __metaclass__ = ABCMeta


class Trait(DescriptiveModel):
    pk = None
    user_pk = None
    utc_timestamp = None
    kind = None
    value = None
    def __init__(self, pk=None, user_pk=None, utc_timestamp=None, kind=None, value=None):
        self.pk = pk
        self.user_pk = user_pk
        self.utc_timestamp = utc_timestamp
        self.kind = kind
        self.value = value
    

class GlucoseLevel(DescriptiveModel):
    pk = None
    user_pk = None
    utc_timestamp = None
    mgdl_level = None
    def __init__(self, pk=None, user_pk=None, utc_timestamp=None, mgdl_level=None):
        self.pk = pk
        self.user_pk = user_pk
        self.utc_timestamp = utc_timestamp
        self.mgdl_level = mgdl_level


class Activity(DescriptiveModel):
    pk = None
    user_pk = None
    utc_timestamp = None
    intensity = None
    minutes = None
    def __init__(self, pk=None, user_pk=None, utc_timestamp=None, intensity=None, minutes=None):
        self.pk = pk
        self.user_pk = user_pk
        self.utc_timestamp = utc_timestamp
        self.intensity = intensity
        self.minutes = minutes


class InsulinAdministration(DescriptiveModel):
    pk = None
    user_pk = None
    utc_timestamp = None
    insulin_type = None
    insulin_units = None
    def __init__(self, pk=None, user_pk=None, utc_timestamp=None, insulin_type=None, insulin_units=None):
        self.pk = pk
        self.user_pk = user_pk
        self.utc_timestamp = utc_timestamp
        self.insulin_type = insulin_type
        self.insulin_units = insulin_units


class Feeding(DescriptiveModel):
    pk = None
    user_pk = None
    utc_timestamp = None
    total_gr = None
    total_ml = None
    carb_gr = None
    protein_gr = None
    fat_gr = None
    fiber_gr = None
    alcohol_gr = None
    def __init__(self, pk=None, user_pk=None, utc_timestamp=None, total_gr=0, total_ml=0, carb_gr=0, protein_gr=0, fat_gr=0, fiber_gr=0, alcohol_gr=0):
        self.pk = pk
        self.user_pk = user_pk
        self.utc_timestamp = utc_timestamp
        self.total_gr = total_gr
        self.total_ml = total_ml
        self.carb_gr = carb_gr
        self.protein_gr = protein_gr
        self.fat_gr = fat_gr
        self.fiber_gr = fiber_gr
        self.alcohol_gr = alcohol_gr



"""
Just enumerations
"""
class TraitKindSexValue:
    MALE = 'male'
    FEMALE = 'female'
    __metaclass__ = ABCMeta
    

class TraitKind:
    BIRTH_UTC_TIMESTAMP = 1 # value accepted is long
    HEIGHT_CM = 2 # value accepted is int
    WEIGHT_KG = 3 # value accepted is float
    NECK_PERIMETER_CM = 4 # value accepted is int
    ABDOMEN_PERIMETER_CM = 5 # value accepted is int
    WAIST_PERIMETER_CM = 6 # value accepted is int
    SEX = 7 # value accepted is one of TraitKindSexValue
    __metaclass__ = ABCMeta


class ActivityIntensity:
    SOFT = 1 # salir a pasear despacio
    MEDIUM = 2 # caminar fuerte ejercicio
    HIGH = 3 # correr al trote, pesas
    EXTREME = 4 # sprints, HIIT, etc
    __metaclass__ = ABCMeta


class InsulinType:
    RAPID = 0
    SHORT = 1
    INTERMEDIATE = 2
    SLOW = 3
    ULTRA_SLOW = 4
    __metaclass__ = ABCMeta


