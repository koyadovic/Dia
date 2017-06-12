# -*- coding: utf-8 -*-
"""
Calculará horas medias de comidas y aperitivos por usuario
Calculará carbohidratos medios de ingesta por usuario
"""
from modules.descriptive.models import InsulinAdministration
from modules.analysis.tools.property import propertycached
from modules.tools.dates import Time, Datetime, Timedelta


"""
A helper class that calculates mean times of main meals.
Also, returns given a time object, what is the nearest meal
or nearest snack to it.

La primera aproximación es mediante las insulinas rápidas o cortas.
Después las horas las calcula con las comidas agrupadas. De esta forma,
si alguien utiliza insulina humana, que ha de esperar para comer,
la hora media de comida será la de la comida real, no la de la administración
de insulina.
"""
class DayTimes(object):
    """"""
    BREAKFAST = 0
    MID_MORNING_SNACK = 1
    """"""
    LUNCH = 2
    AFTERNOON_SNACK = 3
    """"""
    DINNER = 4
    BEFORE_BED_SNACK = 5
    """"""
    ALL_DAY_TIMES = [
        BREAKFAST,
        MID_MORNING_SNACK,
        LUNCH,
        AFTERNOON_SNACK,
        DINNER,
        BEFORE_BED_SNACK
    ]
    
    MEAL_DAY_TIMES = [
        BREAKFAST,
        LUNCH,
        DINNER,
    ]
    
    SNACK_DAY_TIMES = [
        MID_MORNING_SNACK,
        AFTERNOON_SNACK,
        BEFORE_BED_SNACK
    ]

    def __init__(self, context):
        self._c = context
    
    @property
    def user_id(self):
        return self._c.user_id

    @property
    def current_datetime(self):
        return self._c.current_datetime

    @propertycached
    def mean_feeding_hours(self):
        # Hacemos una primera aproximación con las insulinas rápidas o cortas
        # administradas. Allí estarán las comidas
        targets = InsulinAdministration.rapid_short_insulins(
            user_id=self.user_id,
            until_datetime=self.current_datetime,
            order_by_datetime=True,
            limit=30
        )
        
        DAY_HOURS = 24
        DAY_MINUTES = DAY_HOURS * 60
        WIDE_HOURS = 3
        WIDE_MINUTES = WIDE_HOURS * 60

        result = []

        max_i = 0.
        max_mean = 0.
        last_mean = 0.

        for minute in range(0, DAY_MINUTES, 30):
            i = 0.
            total = 0.
            for target in targets:
                minutes = Time.time2minutes(target.datetime)
                if minutes < 180:
                    minutes += DAY_MINUTES
                if minutes >= minute and minutes <= minute + WIDE_MINUTES:
                    i += 1
                    total += minutes
            mean = 0
            if i > 0:
                mean = total / i
            if i > max_i:
                max_mean = mean
                max_i = i
            if last_mean > 0 and mean == 0:
                if max_mean > DAY_MINUTES:
                    max_mean -= DAY_MINUTES
                result.append(max_mean)
                max_mean = 0.
                max_i = 0.
            last_mean = mean
        if max_mean > 0:
            if max_mean > DAY_MINUTES:
                max_mean -= DAY_MINUTES
            result.append(max_mean)

        """
        result es una lista donde:
        result[0] <== desayuno
        result[1] <== comida
        result[2] <== cena
        """
        if len(result) == 3:
            breakfast = Time.minutes2time(result[0])
            lunch = Time.minutes2time(result[1])
            dinner = Time.minutes2time(result[2])
            
            times = type('MeanFeedingHours', (), {})()
            times.breakfast = breakfast
            times.lunch = lunch
            times.dinner = dinner
            
            return times

        return None

    def __str__(self):
        st = """DayTimes:
breakfast: ... {}
lunch: ....... {}
dinner: ...... {}
""".format(
            self.mean_feeding_hours.breakfast,
            self.mean_feeding_hours.lunch,
            self.mean_feeding_hours.dinner,
        )
        return st

    def not_ready(self):
        return self.mean_feeding_hours == None

    def is_ready(self):
        return self.mean_feeding_hours != None
    
    def nearest_meal(self, meal_datetime):
        if not self.mean_feeding_hours:
            return None
        
        base_date = meal_datetime.date()
        if meal_datetime.hour < 3:
            base_date = base_date - Timedelta(days=1)
        
        br = Datetime.combine(base_date, self.mean_feeding_hours.breakfast)
        lu = Datetime.combine(base_date, self.mean_feeding_hours.lunch)
        di = Datetime.combine(base_date, self.mean_feeding_hours.dinner)
        
        result = {
            br: self.BREAKFAST,
            lu: self.LUNCH,
            di: self.DINNER
        }

        nearest = Datetime.nearest_datetime_static(meal_datetime, [br, lu, di])
        return result[nearest]
        

    def nearest_snack(self, snack_datetime):
        if not self.mean_feeding_hours:
            return None

        base_date = snack_datetime.date()
        if snack_datetime.hour < 3:
            base_date = base_date - Timedelta(days=1)
        
        mm = Datetime.combine(base_date, self.mean_feeding_hours.breakfast) + Timedelta(minutes=180)
        af = Datetime.combine(base_date, self.mean_feeding_hours.lunch) + Timedelta(minutes=180)
        bb = Datetime.combine(base_date, self.mean_feeding_hours.dinner) + Timedelta(minutes=180)
        
        result = {
            mm: self.MID_MORNING_SNACK,
            af: self.AFTERNOON_SNACK,
            bb: self.BEFORE_BED_SNACK
        }

        nearest = Datetime.nearest_datetime_static(snack_datetime, [mm, af, bb])
        return result[nearest]


    def previous_day_time(self, dt):
        day_time = self.nearest_day_time(dt) - 1
        if day_time < self.BREAKFAST:
            day_time = self.BEFORE_BED_SNACK
        return day_time

    def next_day_time(self, dt):
        day_time = self.nearest_day_time(dt) + 1
        if day_time > self.BEFORE_BED_SNACK:
            day_time = self.BREAKFAST
        return day_time
        
    def is_meal(self, dt):
        return self.nearest_day_time(dt) in self.MEAL_DAY_TIMES

    def is_snack(self, dt):
        return self.nearest_day_time(dt) in self.SNACK_DAY_TIMES

    def nearest_day_time(self, day_time_datetime):
        if not self.mean_feeding_hours:
            return None

        base_date = day_time_datetime.date()
        if day_time_datetime.hour < 3:
            base_date = base_date - Timedelta(days=1)
        
        br = Datetime.combine(base_date, self.mean_feeding_hours.breakfast)
        lu = Datetime.combine(base_date, self.mean_feeding_hours.lunch)
        di = Datetime.combine(base_date, self.mean_feeding_hours.dinner)
        mm = Datetime.combine(base_date, self.mean_feeding_hours.breakfast) + Timedelta(minutes=180)
        af = Datetime.combine(base_date, self.mean_feeding_hours.lunch) + Timedelta(minutes=180)
        bb = Datetime.combine(base_date, self.mean_feeding_hours.dinner) + Timedelta(minutes=180)
        
        result = {
            br: self.BREAKFAST,
            lu: self.LUNCH,
            di: self.DINNER,
            mm: self.MID_MORNING_SNACK,
            af: self.AFTERNOON_SNACK,
            bb: self.BEFORE_BED_SNACK,
        }

        nearest = Datetime.nearest_datetime_static(day_time_datetime, [br, lu, di, mm, af, bb])
        return result[nearest]

        


