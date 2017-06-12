# -*- coding: utf-8 -*-
from modules.analysis.parameters.carb_dose import CarbsDoses
from modules.analysis.parameters.glucose_dose import GlucoseGramsDose



class ParametersGathering(object):
    """
    Recopila objetos que extraen parámetros
    """
    def __init__(self, context, basic_gathering):
        pass
        #self._c = context
        #self.
        
        #self.carbs_and_doses = CarbsDoses(context, start_dt, end_dt, cf, meal)
        #self.glucose_and_doses = GlucoseGramsDose(carbs_doses, body_traits)
        
        
    @property
    def context(self):
        return self._c