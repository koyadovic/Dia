# -*- coding: utf-8 -*-

from modules.descriptive.models import GlucoseLevel
from modules.analysis.tools.graphs import Graph
from modules.analysis.tools.context import Context
from modules.analysis.tools.stats import LinearRegression
from modules.analysis.groupings.grouped_feedings import GroupedMeal
from modules.analysis.groupings.shape_feedings import Protein, Fat
from modules.tools.dates import Datetime

import numpy as np
import matplotlib.ticker as mticker
from matplotlib.patches import Rectangle


class _CarbsDosesGraph(Graph):
    def __init__(self, parent):
        self.parent = parent
        options = {
            "name": 'carbs_doses_graph',
            "figsize": (8, 6),
#            "dpi": 70,
            "cols": 1,
        }
        super(_CarbsDosesGraph, self).__init__(**options)
        self.add_drawing_routine(self._drawing_routine())
        
    def _drawing_routine(self):
        def draw_routine(ax):
            basal = np.vectorize(lambda carbs: self.parent.min_doses)
            x_carbs = np.linspace(0, 120, 500)
            carbs2dose = np.vectorize(self.parent.carbs2dose)
            y_doses = carbs2dose(x_carbs)
            y_basal_doses = basal(x_carbs)
    
            """
            Dibujamos el gráfico
            """
            tit = ""
            if self.parent._meal == None:
                tit += "Todas las comidas\n"
            elif self.parent._meal == 0:
                tit += "Desayunos\n"
            elif self.parent._meal == 2:
                tit += "Comidas\n"
            elif self.parent._meal == 4:
                tit += "Cenas\n"
            tit += "Desde: {}\nHasta: {}\n".format(self.parent._start_dt, self.parent._end_dt)
            tit += u"Carbohidratos (g) / Insulina (u) / 2 horas"
            ax.set_title(tit)
                
            ax.set_xlabel(u"Carbohidratos")
            ax.set_ylabel(u"Insulina")
    
            ax.set_xlim(0, 120)
            ax.set_ylim(0, 25)
            ax.set_xticks(np.arange(0, 120., 15.))
            ax.set_yticks(np.arange(0, 25., 4.))
    
            ax.xaxis.set_major_formatter(mticker.FormatStrFormatter('$%dg$'))
            ax.yaxis.set_major_formatter(mticker.FormatStrFormatter('$%du$'))
    
            ax.scatter(np.array(self.parent._x_carbs), np.array(self.parent._y_doses), color='blue', marker='o', alpha=0.2)
    
            utotallegend = None
            if self.parent.b >= 0:
                utotallegend, = ax.plot(x_carbs[y_doses>=y_basal_doses], y_doses[y_doses>=y_basal_doses], label="$u_{Total} = " + "{}g + {}$".format(round(self.parent.m, 4), round(self.parent.b, 4)))
            else:
                utotallegend, = ax.plot(x_carbs[y_doses>=y_basal_doses], y_doses[y_doses>=y_basal_doses], label="$u_{Total} = " + "{}g {}$".format(round(self.parent.m, 4), round(self.parent.b, 4)))
    
            ubasallegend, = ax.plot(x_carbs[y_doses<=y_basal_doses], y_basal_doses[y_doses<=y_basal_doses], label="$u_{Basal} = " + str(round(self.parent.min_doses, 4)) + "$")
            ax.fill_between(x_carbs, y_basal_doses, color='green', alpha=0.1)
            ax.fill_between(x_carbs[y_doses>y_basal_doses], y_doses[y_doses>y_basal_doses], y_basal_doses[y_doses>y_basal_doses], color='blue', alpha=0.1)
    
            umblegend = Rectangle((0, 0), 1, 1, fc="w", fill=False, edgecolor='none', linewidth=0, label='$m = ' + '{}'.format(round(self.parent.m, 4)) + ', b = ' + '{}$'.format(round(self.parent.b, 4)))
            ucfklegend = Rectangle((0, 0), 1, 1, fc="w", fill=False, edgecolor='none', linewidth=0, label='$c = ' + '{}'.format(round(self.parent._cf, 4)) + ', k = ' + '{}$'.format(round(self.parent.k, 4)))
            
            ax.legend(loc='upper left', handles=[umblegend, ucfklegend, utotallegend, ubasallegend])
            ax.grid()
        
        return lambda ax: draw_routine(ax)



class CarbsDoses(object):

    def __init__(self, context, start_dt, end_dt, cf, meal=None):
        assert isinstance(context, Context), "context no es una instancia válida de Context"
        assert isinstance(start_dt, Datetime) and isinstance(end_dt, Datetime), "start_dt y end_dt han de ser instancias válidas datetime"
        assert (start_dt - end_dt).total_seconds() <= 0, "start_dt {} ha de ser anterior a end_dt {}".format(start_dt, end_dt)
        
        self._context = context
        
        self._start_dt = start_dt
        self._end_dt = end_dt
        self._cf = cf
        
        self._meal = meal
        self._m = None
        self._b = None
        
        self._grouped_meals = None
        
        self.graph = _CarbsDosesGraph(self)
    
    @property
    def grouped_meals(self):
        """
        + Hay que intentar tomar datos con grouped meals sin actividad con glucosa de antes en rango
        + Hay que añadir grouped meals con o sin actividad con glucosa antes en rango, la de después alto.
        """
        if self._grouped_meals == None:
            self._grouped_meals = []
            options = {
                    'user_id': self._context.user_id,
                    'from_datetime': self._start_dt,
                    'until_datetime': self._end_dt,
                    'glucose_before_above_range': False,
                    'with_activity': False,
                    'meal': self._meal
            }
            result = GroupedMeal.last_grouped_meals(**options)
            if result != None:
                self._grouped_meals += result
            
            options = {
                    'user_id': self._context.user_id,
                    'from_datetime': self._start_dt,
                    'until_datetime': self._end_dt,
                    'glucose_before_above_range': False,
                    'glucose_after_above_range': True,
                    'meal': self._meal
            }
            result = GroupedMeal.last_grouped_meals(**options)
            if result != None:
                self._grouped_meals += result
            
        return self._grouped_meals
    
    
    def _calculate_parameters(self):
        if len(self.grouped_meals) == 0:
            return
        
        min_doses = []
        x_carbs = []
        y_doses = []

        for meal in self.grouped_meals:
            meal_dose = 0.
            
            protein = Protein(meal.protein_gr)
            fat = Fat(meal.fat_gr)
            
            carbs = meal.carb_gr

            meal_dose += meal.basal_insulin
            meal_dose += meal.prandial_insulin
            meal_dose -= (meal.glucose_level_before - GlucoseLevel.TARGET_GLUCOSE_LEVEL_0) / self._cf
            meal_dose += ((meal.glucose_level_after - protein.deviation - fat.deviation) - GlucoseLevel.TARGET_GLUCOSE_LEVEL_120) / self._cf
            
            min_doses.append(meal.basal_insulin)
            
            x_carbs.append(carbs)
            y_doses.append(meal_dose)
        
        regression = LinearRegression(x_carbs, y_doses)
        
        if regression.m > 0.:
            self._m = regression.m
            self._b = regression.b
            self._x_carbs = x_carbs
            self._y_doses = y_doses
        
        if len(min_doses) > 0:
            self._min_doses = sum(min_doses) / len(min_doses)


    @property
    def m(self):
        """
        Slope of the function
        """
        if self._m == None or self._b == None:
            self._calculate_parameters()
        return self._m

    @property
    def b(self):
        """
        b param of the linear function
        """
        if self._m == None or self._b == None:
            self._calculate_parameters()
        return self._b

    
    @property
    def k(self):
        """
        Constante de la relación de proporcionalidad inversa que mantienen el cf y m
        """
        if self._m == None or self._b == None:
            self._calculate_parameters()

        if self.m != None and self.m > 0.:
            return self._cf * self.m

        return None


    @property
    def min_carbs(self):
        if self._m == None or self._b == None:
            self._calculate_parameters()

        if self._m == None or self._b == None:
            return 0.
        
        return self.dose2carbs(self._min_doses)
    
    @property
    def min_doses(self):
        return self._min_doses
    
    
    """
    para pillar carbs dese una dosis o dosis desde unos gr de carbs concretos.
    """
    def carbs2dose(self, carbs):
        return (carbs * self.m) + self.b

    def dose2carbs(self, dose):
        return (dose - self.b) / self.m
    
        






















    