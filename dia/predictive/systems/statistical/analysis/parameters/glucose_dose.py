# -*- coding: utf-8 -*-

from modules.analysis.parameters.carb_dose import CarbsDoses
from modules.analysis.basics.bodytraits import BodyTraits
from modules.analysis.tools.context import Context
from modules.tools.dates import Datetime
from modules.analysis.basics.cfrules import CorrectionFactorRules


class GlucoseGramsDose(object):
    
    def __init__(self, carbs_doses, body_traits):
        assert isinstance(carbs_doses, CarbsDoses), "carbs_doses instancia inválida"
        assert isinstance(body_traits, BodyTraits), "body_traits instancia inválida"
        
        self.carbs_doses = carbs_doses
        self.body_traits = body_traits
    
    
    def carbs2glucosegr(self, carbs):
        return (carbs * self.carbs_doses.k * 10. * self.body_traits.blood_liters) / 1000.

    def glucosegr2carbs(self, glucosegr):
        return (glucosegr * 1000.) / self.carbs_doses.k / 10. / self.body_traits.blood_liters
    
    def dose2glucosegr(self, dose):
        
        carbs = self.carbs_doses.dose2carbs(dose)
        return self.carbs2glucosegr(carbs)

    def glucosegr2dose(self, glucosegr):
        carbs = self.glucosegr2carbs(glucosegr)
        return self.carbs_doses.carbs2dose(carbs)


    def glucosegr2mgdl(self, glucosegr):
        return (glucosegr * 1000.) / 10. / self.body_traits.blood_liters


    def mgdl2glucosegr(self, mgdl):
        return (mgdl * 10. * self.body_traits.blood_liters) / 1000.



def main():
    context = Context(1, Datetime(2017, 01, 10, 20, 0))
    body = BodyTraits(context)
    cfrules = CorrectionFactorRules(context)
    carbs_doses = CarbsDoses(context, Datetime(2017, 01, 1, 20, 0), Datetime(2017, 01, 10, 20, 0), cfrules.rule2000, 4)
    
    glucose_grams_per_dose = GlucoseGramsDose(carbs_doses, body)
    print "50gr de hidrato son {}gr de glucosa".format(glucose_grams_per_dose.carbs2glucosegr(50.))
    print "10 unidades de insulina cubren {} gr de glucosa".format(glucose_grams_per_dose.dose2glucosegr(10.))
    
    import sys
    sys.exit()


if __name__ == "__main__":
    main()









