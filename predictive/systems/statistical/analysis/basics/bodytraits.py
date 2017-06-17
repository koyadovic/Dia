# -*- coding: utf-8 -*-
from ...analysis.tools.property import propertycached
from ...tools.dates import Datetime, Timedelta

from dia.models import TraitKind, TraitKindSexValue
from dia.core import diacore



class BodyTraits(object):
    
    def __init__(self, context):
        self._c = context

    def __str__(self):
        s = """BodyTraits:
sex ........................ {}
height ..................... {} cm
weight ..................... {} kg
neck ....................... {} cm
abdomen .................... {} cm
waist ...................... {} cm
age ........................ {} years
activity_footprint ......... {}
kcal_needs ................. {} Kcal/day
fat_percentage ............. {} %
imc ........................ {}
waist_height_ratio ......... {}
blood_liters ............... {} L
""".format(
            self.sex,
            round(self.height),
            round(self.weight),
            round(self.neck),
            round(self.abdomen),
            round(self.waist),
            self.age,
            round(self.activity_footprint, 1),
            int(round(self.kcal_needs)),
            round(self.fat_percentage, 2),
            round(self.imc, 2),
            round(self.waist_height_ratio, 2),
            round(self.blood_liters, 1),
        )
        return s

    @property
    def user_pk(self):
        return self._c.user_pk

    @property
    def current_datetime(self):
        return self._c.current_datetime

    @staticmethod
    def _float(parameter):
        if parameter != "":
            return float(parameter)
        else:
            return 0.0

    @staticmethod
    def _int(parameter):
        if parameter != "":
            return int(parameter)
        else:
            return 0
        
    @propertycached
    def sex(self):
        try:
            return diacore.get_traits(user_pk=self.user_pk, kind=TraitKind.SEX, order_ascending=False, limit=1)[0]
        except IndexError:
            return None
    
    @propertycached
    def height(self):
        try:
            return diacore.get_traits(user_pk=self.user_pk, kind=TraitKind.HEIGHT_CM, order_ascending=False, limit=1)[0]
        except IndexError:
            return None
    
    @propertycached
    def weight(self):
        try:
            return diacore.get_traits(user_pk=self.user_pk, kind=TraitKind.WEIGHT_KG, order_ascending=False, limit=1)[0]
        except IndexError:
            return None

    @propertycached
    def neck(self):
        try:
            return diacore.get_traits(user_pk=self.user_pk, kind=TraitKind.NECK_PERIMETER_CM, order_ascending=False, limit=1)[0]
        except IndexError:
            return None

    @propertycached
    def abdomen(self):
        try:
            return diacore.get_traits(user_pk=self.user_pk, kind=TraitKind.ABDOMEN_PERIMETER_CM, order_ascending=False, limit=1)[0]
        except IndexError:
            return None

    @propertycached
    def waist(self):
        try:
            return diacore.get_traits(user_pk=self.user_pk, kind=TraitKind.WAIST_PERIMETER_CM, order_ascending=False, limit=1)[0]
        except IndexError:
            return None

    @propertycached
    def age(self):
        try:
            birth_utc_timestamp = diacore.get_traits(user_pk=self.user_pk, kind=TraitKind.BIRTH_UTC_TIMESTAMP, order_ascending=False, limit=1)[0]
        except IndexError:
            return None

        timedelta = self.current_datetime - Datetime.utcfromtimestamp(birth_utc_timestamp)
        return timedelta.total_years
    
    @propertycached
    def activity_footprint(self):
        
        activities = diacore.get_activities(
            user_pk=self.user_pk,
            from_utc_timestamp=(self.current_datetime - Timedelta(days=30)).utc_timestamp
        )

        last_day = 0
        max_intensity = 0
        footprints = []
    
        for activity in activities:
            activity_datetime = Datetime.utcfromtimestamp(activity.utc_timestamp)
            if last_day != 0 and activity_datetime.day != last_day:
                last_day = activity_datetime.day
                footprints.append((max_intensity/4.)*10.)
                max_intensity = 0
    
            if activity.intensity > max_intensity:
                max_intensity = activity.intensity
    
            if last_day == 0:
                last_day = activity_datetime.day
        r = 0
        if len(footprints) > 0:
            r = float(sum(footprints)) / float(len(footprints))
        return r
    
    @property
    def kcal_needs(self):
        params = {}
        params[TraitKindSexValue.MALE] = {
            'sum_number': 66.,
            'weight': 13.7,
            'height': 5.,
            'age': 6.8
        }
        params[TraitKindSexValue.FEMALE] = {
            'sum_number': 655.,
            'weight': 9.6,
            'height': 1.8,
            'age': 4.7
        }
        
        calculator = lambda sex, weight_kg, height_cm, age, activity_factor: (params[sex]['sum_number'] + \
            (params[sex]['weight'] * weight_kg)) + ((params[sex]['height'] * height_cm) - \
                (params[sex]['age'] * age)) * activity_factor
        
        activity_factor = (self.activity_footprint * 0.07) + 1.2

        return calculator(
            self.sex, self.weight, self.height, self.age, activity_factor)

    
    @property
    def fat_percentage(self):
        params = {}
        params[TraitKindSexValue.MALE] = {
            'abdomen': 0.69,
            'height': -0.157,
            'neck': -0.7429,
            'waist': 0.0,
            'independent': 14.2
        }
        params[TraitKindSexValue.FEMALE] = {
            'abdomen': 0.47,
            'height': -0.25,
            'neck': -0.51,
            'waist': 0.47,
            'independent': 5.75
        }
        percentage = lambda sex, abdomen, height, neck, waist: (params[sex]['abdomen'] * abdomen) + \
            (params[sex]['height'] * height) + (params[sex]['neck'] * neck) + \
            (params[sex]['waist'] * waist) + params[sex]['independent']
        
        """
        Extraemos estimación de porcentaje de grasa corporal
        """
        return percentage(
            self.sex, self.abdomen, self.height, self.neck, self.waist)
    

        
    @property        
    def imc(self):
        return self.weight / ((self.height / 100.) ** 2)
    
    @property
    def waist_height_ratio(self):
        """
        NOTA: > 0.5, más riesgos para la salud
        """
        return self.abdomen / self.height
    
    @property
    def blood_liters(self):
        ideal_weight = self.weight - (self.weight * (self.fat_percentage / 100.)) + (self.weight * (20. / 100.)) 
        
        estimation1 = (ideal_weight * 70.) / 1000.
        estimation2 = (ideal_weight / 13.)
        
        return (estimation1 + estimation2) / 2.0
        

