from abc import ABCMeta



class DescriptiveModel(ABCMeta):
    pass


class Trait(DescriptiveModel):
    pk = None
    user_pk = None
    utc_timestamp = None
    kind = None
    value = None
    

class GlucoseLevel(DescriptiveModel):
    pk = None
    user_pk = None
    utc_timestamp = None
    mgdl_level = None


class Activity(DescriptiveModel):
    pk = None
    user_pk = None
    utc_timestamp = None
    intensity = None
    minutes = None


class InsulinAdministration(DescriptiveModel):
    pk = None
    user_pk = None
    utc_timestamp = None
    insulin_type = None
    insulin_units = None


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



"""
Just enumerations
"""
class TraitKindSexValue():
    MALE = 'male'
    FEMALE = 'female'
    

class TraitKind():
    BIRTH_UTC_TIMESTAMP = 1 # value accepted is long
    HEIGHT_CM = 2 # value accepted is int
    WEIGHT_KG = 3 # value accepted is float
    NECK_PERIMETER_CM = 4 # value accepted is int
    ABDOMEN_PERIMETER_CM = 5 # value accepted is int
    WAIST_PERIMETER_CM = 6 # value accepted is int
    SEX = 7 # value accepted is one of TraitKindSexValue


class ActivityIntensity():
    SOFT = 1 # salir a pasear despacio
    MEDIUM = 2 # caminar fuerte ejercicio
    HIGH = 3 # correr al trote, pesas
    EXTREME = 4 # sprints, HIIT, etc


class InsulinType():
    RAPID = 0
    SHORT = 1
    INTERMEDIATE = 2
    SLOW = 3
    ULTRA_SLOW = 4
