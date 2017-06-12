# -*- coding: utf-8 -*-
from modules.descriptive.models import InsulinAdministration
from modules.analysis.tools.property import propertycached
from modules.tools.dates import Timedelta

class CorrectionFactorRules(object):

    def __init__(self, context):
        self._c = context

        self._total_count = None
        self._range_hours_count = None
    
    
    @property
    def user_id(self):
        return self._c.user_id

    @property
    def current_datetime(self):
        return self._c.current_datetime


    @propertycached
    def _insulins(self):
        insulins = InsulinAdministration.all_insulins(
            user_id=self.user_id,
            until_datetime=self.current_datetime,
            order_by_datetime=True,
            limit=40,
        )
        if insulins == None:
            return []
        return insulins
        
    @property
    def _total(self):
        if self._total_count != None:
            return self._total_count

        total = 0.
        for insulin in self._insulins:
            total += insulin.dose

        self._total_count = total
        return self._total_count

    @property
    def _range_hours(self):
        if self._range_hours_count != None:
            return self._range_hours_count

        end_hours = {
            InsulinAdministration.TYPE_RAPID: 3,
            InsulinAdministration.TYPE_SHORT: 5,
            InsulinAdministration.TYPE_INTERMEDIATE: 10,
            InsulinAdministration.TYPE_SLOW: 20,
            InsulinAdministration.TYPE_ULTRA_SLOW: 45,
            
        }
        start_dt = None
        end_dt = None
        for insulin in self._insulins:
            if start_dt == None:
                start_dt = insulin.datetime
                
            temp_end_dt = insulin.datetime + Timedelta(hours=end_hours[insulin.type])
            if end_dt == None or temp_end_dt > end_dt:
                end_dt = temp_end_dt
        
        range_hours = (end_dt - start_dt).total_seconds() / 60. / 60.

        self._range_hours_count = range_hours
        return self._range_hours_count
    
    def __str__(self):
        s = """CorrectionFactorRules:
1600 rule: {}
1800 rule: {}
2000 rule: {}
""".format(self.rule1600, self.rule1800, self.rule2000)
        return s
    
    @property
    def rule1600(self):
        if self._range_hours > 20 and self._total > 0.:
            return 1600 / (24. / self._range_hours) / self._total
                
    @property
    def rule1800(self):
        if self._range_hours > 20 and self._total > 0.:
            return 1800 / (24. / self._range_hours) / self._total
                
    @property
    def rule2000(self):
        if self._range_hours > 20 and self._total > 0.:
            return 2000 / (24. / self._range_hours) / self._total
                
        
