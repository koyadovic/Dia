# -*- coding: utf-8 -*-
from modules.analysis.basics.bodytraits import BodyTraits
from modules.analysis.basics.daytimes import DayTimes
from modules.analysis.basics.cfrules import CorrectionFactorRules
from modules.analysis.basics.basalinsulin import BasalInsulin
from modules.analysis.basics.hba1c import HbA1c


class BasicGathering(object):
    
    def __init__(self, context):
        self._c = context
        
        """
        Independents
        """
        self.daytimes = DayTimes(context)
        self.body = BodyTraits(context)
        self.cfrules = CorrectionFactorRules(context)
        self.hba1c = HbA1c(context)

        """
        Dependents
        """
        self.basalinsulin = BasalInsulin(context, self.daytimes)
        
    def __str__(self):
        s = "{}\n{}\n{}\n{}\n{}\n".format(
            self.daytimes,
            self.body,
            self.cfrules,
            self.basalinsulin,
            self.hba1c
        )
        return s
    
    @property
    def context(self):
        return self._c
    
#     @property
#     def user_id(self):
#         return self._c.user_id
# 
#     @property
#     def current_datetime(self):
#         return self._c.current_datetime
