# -*- coding: utf-8 -*-
from modules.descriptive.events import on_glucose_inserted
from modules.descriptive.models import InsulinAdministration
from modules.descriptive.models import GlucoseLevel, Feeding, Activity

from modules.tools.dates import Timedelta, Datetime
from modules.tools.shapes import Shape

from modules.analysis.groupings.shape_feedings import ShapeFeeding
from modules.analysis.groupings.shape_insulins import ShapeInsulin

from modules.analysis.bundles.basics import BasicGathering
from modules.analysis.basics.daytimes import DayTimes

from modules.analysis.tools.context import Context
from modules.analysis.tools.stats import QuadraticInterpolation
from modules.analysis.tools.graphs import Graph

import matplotlib.patches as mpatches
import matplotlib.ticker as mticker
import numpy as np



from sqlalchemy.ext.hybrid import hybrid_property

# MODELOS
################################################################################
"""
Modelos especificos de la herramienta
"""
from modules.analysis.model import engine as predictive_engine
from modules.analysis.model import analysis_session
from sqlalchemy import Column, Integer, Float, DateTime
from sqlalchemy import and_, or_
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base(predictive_engine)


class GroupedMeal(Base):
    """
    Agrupa en las glucosas de después de comer
    todo lo que involucró a la comida en esas dos horas.
    macronutrientes digeridos, glucosas antes y después
    de esas dos horas e insulina absorvida.
    """
    """"""
    __tablename__ = 'analysis_groupings_meals'

    """"""
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False, index=True)
    _datetime = Column(DateTime, nullable=False, index=True)
    meal = Column(Integer, nullable=False, index=True)

    """
    meal intake
    """
    carb_gr = Column(Float, nullable=False)
    protein_gr = Column(Float, nullable=False)
    fat_gr = Column(Float, nullable=False)
    fiber_gr = Column(Float, nullable=False)
    alcohol_gr = Column(Float, nullable=False)

    """
    Insulin acting
    """
    prandial_insulin = Column(Float, nullable=False)
    basal_insulin = Column(Float, nullable=False)

    """
    Glucose levels
    """
    glucose_level_before = Column(Float, nullable=False, index=True)
    glucose_level_after = Column(Float, nullable=False, index=True)

    """
    Activity minutes
    """
    intensity_soft_minutes = Column(Integer, nullable=False, default=0, index=True)
    intensity_medium_minutes = Column(Integer, nullable=False, default=0, index=True)
    intensity_high_minutes = Column(Integer, nullable=False, default=0, index=True)
    intensity_extreme_minutes = Column(Integer, nullable=False, default=0, index=True)
    

    def __str__(self):
        st = """GroupedMeal: user_id: {}, datetime: {}, meal: {}, carb_gr: {},
protein_gr: {}, fat_gr: {}, fiber_gr: {}, alcohol_gr: {}, prandial_insulin: {},
basal_insulin: {}, glucose_level_before: {}, glucose_level_after: {},
intensity_soft_minutes: {}, intensity_medium_minutes: {}, intensity_high_minutes: {},
intensity_extreme_minutes: {}""".format(
            self.user_id,
            self.datetime,
            self.meal,
            self.carb_gr,
            self.protein_gr,
            self.fat_gr,
            self.fiber_gr,
            self.alcohol_gr,
            self.prandial_insulin,
            self.basal_insulin,
            self.glucose_level_before,
            self.glucose_level_after,
            self.intensity_soft_minutes,
            self.intensity_medium_minutes,
            self.intensity_high_minutes,
            self.intensity_extreme_minutes,
        )
        return st

    @hybrid_property
    def datetime(self):
        return DateTime(self._datetime.year, self._datetime.month, self._datetime.day, self._datetime.hour, self._datetime.minute, self._datetime.second)
    
    @datetime.setter
    def datetime(self, value):
        self._datetime = value
    
    @classmethod
    def last_grouped_meals(cls, **kvargs):
        options = {
                'user_id': None,
                'from_datetime': None,
                'until_datetime': None,
                'glucose_before_above_range': None,
                'glucose_after_above_range': None,
                'with_activity': None,
                'order_by_datetime': True,
                'desc_order': False,
                'limit': None,
                'meal': None }
    
        options.update(kvargs)
        
        if options['user_id'] == None:
            return None

        se = analysis_session()
        r_query = se.query(GroupedMeal).\
            filter(GroupedMeal.user_id == options['user_id'])


        """
        Dates
        """
        if options['until_datetime'] != None:        
            r_query = r_query.filter(GroupedMeal._datetime <= options['until_datetime'])
        
        if options['from_datetime'] != None:        
            r_query = r_query.filter(GroupedMeal._datetime >= options['from_datetime'])

        """
        Glucoses ranges
        """        
        if options['glucose_before_above_range'] != None and options['glucose_before_above_range']:
            r_query = r_query.\
                filter(GroupedMeal.glucose_level_before > GlucoseLevel.TARGET_GLUCOSE_LEVEL_0 + 20)

        if options['glucose_before_above_range'] != None and not options['glucose_before_above_range']:
            r_query = r_query.\
                filter(GroupedMeal.glucose_level_before <= GlucoseLevel.TARGET_GLUCOSE_LEVEL_0 + 20)

        if options['glucose_after_above_range'] != None and options['glucose_after_above_range']:
            r_query = r_query.\
                filter(GroupedMeal.glucose_level_after > GlucoseLevel.TARGET_GLUCOSE_LEVEL_120 + 20)

        if options['glucose_after_above_range'] != None and not options['glucose_after_above_range']:
            r_query = r_query.\
                filter(GroupedMeal.glucose_level_after <= GlucoseLevel.TARGET_GLUCOSE_LEVEL_120 + 20)
        
        if options['with_activity'] != None and options['with_activity']:
            r_query = r_query.\
                filter(
                    or_(
                        GroupedMeal.intensity_soft_minutes > 0.,
                        GroupedMeal.intensity_medium_minutes > 0.,
                        GroupedMeal.intensity_high_minutes > 0.,
                        GroupedMeal.intensity_extreme_minutes > 0.,
                    )
                )

        if options['with_activity'] != None and not options['with_activity']:
            r_query = r_query.\
                filter(
                    and_(
                        GroupedMeal.intensity_soft_minutes == 0.,
                        GroupedMeal.intensity_medium_minutes == 0.,
                        GroupedMeal.intensity_high_minutes == 0.,
                        GroupedMeal.intensity_extreme_minutes == 0.,
                    )
                )

        if options['meal'] != None:        
            r_query = r_query.filter(GroupedMeal.meal == options['meal'])
            
        if options['order_by_datetime']:
            if options['desc_order']:
                r_query = r_query.order_by(GroupedMeal._datetime.desc())
            else:
                r_query = r_query.order_by(GroupedMeal._datetime)

        if options['limit'] != None:     
            r_query = r_query.limit(options['limit'])
        
        return r_query.all()



class GroupedSnack(Base):
    """"""
    __tablename__ = 'analysis_groupings_snacks'

    """"""
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False, index=True)
    _datetime = Column(DateTime, nullable=False, index=True)
    snack = Column(Integer, nullable=False, index=True)

    glucose_level_before = Column(Float, nullable=False, index=True)
    glucose_level_after = Column(Float, nullable=False, index=True)

    minutes_until_next_meal = Column(Integer, nullable=False)
    carb_gr = Column(Float, nullable=False)
    protein_gr = Column(Float, nullable=False)
    fat_gr = Column(Float, nullable=False)
    fiber_gr = Column(Float, nullable=False)
    alcohol_gr = Column(Float, nullable=False)

    prandial_insulin = Column(Float, nullable=False)
    basal_insulin = Column(Float, nullable=False)
    
    """
    Activity minutes
    """
    intensity_soft_minutes = Column(Integer, nullable=False, default=0)
    intensity_medium_minutes = Column(Integer, nullable=False, default=0)
    intensity_high_minutes = Column(Integer, nullable=False, default=0)
    intensity_extreme_minutes = Column(Integer, nullable=False, default=0)

    def __str__(self):
        st = """GroupedSnack: user_id: {}, datetime: {}, snack: {},
glucose_deviation_before: {}, glucose_deviation_result: {},
minutes_until_next_meal: {}, carb_gr: {}, protein_gr: {},
fat_gr: {}, fiber_gr: {}, alcohol_gr: {}, prandial_insulin: {},
basal_insulin: {}, intensity_soft_minutes: {}, intensity_medium_minutes: {},
intensity_high_minutes: {}, intensity_extreme_minutes: {},""".format(
            self.user_id,
            self.datetime,
            self.snack,
            self.glucose_deviation_before,
            self.glucose_deviation_result,
            self.minutes_until_next_meal,
            self.carb_gr,
            self.protein_gr,
            self.fat_gr,
            self.fiber_gr,
            self.alcohol_gr,
            self.prandial_insulin,
            self.basal_insulin,
            self.intensity_soft_minutes,
            self.intensity_medium_minutes,
            self.intensity_high_minutes,
            self.intensity_extreme_minutes,
        )
        return st

    @hybrid_property
    def datetime(self):
        return Datetime(self._datetime.year, self._datetime.month, self._datetime.day, self._datetime.hour, self._datetime.minute, self._datetime.second)
    
    @datetime.setter
    def datetime(self, value):
        self._datetime = value

    @classmethod
    def last_grouped_snacks(cls, **kvargs):
        options = {
                'user_id': None,
                'from_datetime': None,
                'until_datetime': None,
                'order_by_datetime': True,
                'desc_order': False,
                'limit': None,
                'snack': None }
    
        options.update(kvargs)
        
        if options['user_id'] == None:
            return None

        se = analysis_session()
        r_query = se.query(GroupedSnack).\
            filter(GroupedSnack.user_id == options['user_id'])

        r_query = r_query.order_by(GroupedSnack._datetime.desc())
        
        if options['from_datetime'] != None:        
            r_query = r_query.filter(GroupedSnack._datetime >= options['from_datetime'])

        if options['until_datetime'] != None:        
            r_query = r_query.filter(GroupedSnack._datetime <= options['until_datetime'])

        if options['snack'] != None:        
            r_query = r_query.filter(GroupedSnack.snack == options['snack'])

        if options['order_by_datetime']:
            if options['desc_order']:
                r_query = r_query.order_by(GroupedSnack._datetime.desc())
            else:
                r_query = r_query.order_by(GroupedSnack._datetime)

        if options['limit'] != None:     
            r_query = r_query.limit(options['limit'])
        
        return r_query.all()


Base.metadata.create_all(checkfirst=True)


# FIN DE LOS MODELOS
################################################################################



class NutrientsDigested(Graph):
    def __init__(self, **kvargs):
        options = {
            "name": 'nutrients_digested',
            "figsize": (12, 10),
#            "dpi": 70,
            "cols": 1,
        }
        super(NutrientsDigested, self).__init__(**options)

        self._context = kvargs['context']
        self._start_dt = kvargs['start_dt']
        self._end_dt = kvargs['end_dt']

        self._recalculate()

        """
        Rutinas de dibujado
        """
        self.add_drawing_routine(self._drawing_routine('carb'))
        self.add_drawing_routine(self._drawing_routine('protein'))
        self.add_drawing_routine(self._drawing_routine('fat'))

    def _recalculate(self):
        """
        Recuperamos los feedings
        """
        feedings = Feeding.last_feedings(
            user_id=self._context.user_id,
            from_datetime=self._start_dt - Timedelta(hours=6),
            until_datetime=self._end_dt
        )
        
        shape_feedings = [ShapeFeeding(feeding) for feeding in feedings]
        
        feedings_accumulated = []
        
    
        for feeding in shape_feedings:
           
            pending_total_gr = 0.
            pending_carb_gr = 0.
            pending_protein_gr = 0.
            pending_fat_gr = 0.
            
            for accumulated in feedings_accumulated:
                accumulated_end_dt = accumulated.datetime + Timedelta(minutes=accumulated.fat.end_x)
                if accumulated_end_dt > feeding.datetime:
                    minutes = int(round((feeding.datetime - accumulated.datetime).total_seconds() / 60.))
    
                    accumulated.carbohydrate.pointers(0, minutes)
                    accumulated.protein.pointers(0, minutes)
                    accumulated.fat.pointers(0, minutes)
    
                    pending_carb_gr += accumulated.carbohydrate.digestion_pending
                    pending_protein_gr += accumulated.protein.digestion_pending
                    pending_fat_gr += accumulated.fat.digestion_pending
    
                    if accumulated.is_solid:
                        """
                        Se trata de un sólido
                        """
                        factor = (
                            accumulated.carbohydrate.digestion_pending + \
                            accumulated.protein.digestion_pending + \
                            accumulated.fat.digestion_pending
                        ) / (
                            accumulated.carbohydrate.gr + \
                            accumulated.protein.gr + \
                            accumulated.fat.gr
                        )
                        
                        if factor > 1.0: factor = 1.0
    
                        pending_total_gr += accumulated.total_gr * factor
            
            feeding.scale_digestion_time(pending_total_gr, pending_carb_gr, pending_protein_gr, pending_fat_gr)
            #feeding.graph.show()
            feedings_accumulated.append(feeding)
        
    
        """
        Aquí empieza el cálculo de lo digerido
        """
        carb_shape_sum_acumulated = None
        protein_shape_sum_acumulated = None
        fat_shape_sum_acumulated = None
        
        """
        lista que guarda el primer shape,
        la suma de los dos primeros, la suma de los tres primeros, etcétera
        """
        carb_shapes_list = []
        protein_shapes_list = []
        fat_shapes_list = []
        
        """
        Totales digeridos en el rango solicitado
        """
        self.carb_total_gr = 0.
        self.protein_total_gr = 0.
        self.fat_total_gr = 0.
        
        """
        Para dibujar en cada instante qué fue ingerido
        """
        self.feeding_hours = []
        self.carb_g = []
        self.protein_g = []
        self.fat_g = []
        self.fiber_g = []
        self.alcohol_g = []
        
        for feeding in shape_feedings:
            carb_shape, protein_shape, fat_shape = feeding.relative_positioned_shapes(self._start_dt)
            
            self.feeding_hours.append(feeding._feeding.datetime)
            self.carb_g.append(feeding._feeding.carb_gr)
            self.protein_g.append(feeding._feeding.protein_gr)
            self.fat_g.append(feeding._feeding.fat_gr)
            self.fiber_g.append(feeding._feeding.fiber_gr)
            self.alcohol_g.append(feeding._feeding.alcohol_gr)
            
            if carb_shape_sum_acumulated == None:
                carb_shape_sum_acumulated = carb_shape
            else:
                carb_shape_sum_acumulated = Shape.sum_shapes_y(carb_shape_sum_acumulated, carb_shape)
            carb_shapes_list.append(carb_shape_sum_acumulated)
            self.carb_total_gr += feeding._feeding.carb_gr
    
            if protein_shape_sum_acumulated == None:
                protein_shape_sum_acumulated = protein_shape
            else:
                protein_shape_sum_acumulated = Shape.sum_shapes_y(protein_shape_sum_acumulated, protein_shape)
            protein_shapes_list.append(protein_shape_sum_acumulated)
            self.protein_total_gr += feeding._feeding.protein_gr
    
            if fat_shape_sum_acumulated == None:
                fat_shape_sum_acumulated = fat_shape
            else:
                fat_shape_sum_acumulated = Shape.sum_shapes_y(fat_shape_sum_acumulated, fat_shape)
            fat_shapes_list.append(fat_shape_sum_acumulated)
            self.fat_total_gr += feeding._feeding.fat_gr
        
    
        """
        Shapes resultado de la suma de todos los shapes de los alimentos ingeridos anteriormente
        """
        self.carb_shape = carb_shapes_list[-1]
        self.protein_shape = protein_shapes_list[-1]
        self.fat_shape = fat_shapes_list[-1]
        
        """
        Grafico de apilado de alimentos ingeridos
        """
        carb = Shape(carb_shape)
        protein = Shape(protein_shape)
        fat = Shape(fat_shape)
        end_min = (self._end_dt - self._start_dt).total_mins
        carb.pointers(0, end_min)
        protein.pointers(0, end_min)
        fat.pointers(0, end_min)
        
        self.digested_ch_gr = carb.value_inside_pointers(self.carb_total_gr)
        self.digested_pr_gr = protein.value_inside_pointers(self.protein_total_gr)
        self.digested_fa_gr = fat.value_inside_pointers(self.fat_total_gr)
        self.digested_fiber = 0.
        self.digested_alcohol = 0.
    
        for feeding in shape_feedings:
            after_start = feeding._feeding.datetime >= self._start_dt
            before_end = feeding._feeding.datetime <= self._end_dt
            if after_start and before_end:
                self.digested_fiber += feeding._feeding.fiber_gr
                self.digested_alcohol += feeding._feeding.alcohol_gr
            
        factor = (self.digested_ch_gr + self.digested_pr_gr + self.digested_fa_gr) / (self.carb_total_gr + self.protein_total_gr + self.fat_total_gr)
        self.digested_fiber *= factor
        self.digested_alcohol *= factor

        

    def _drawing_routine(self, what=''):
        assert what in ["carb", "protein", "fat"]

        def draw_routine(ax):
            """
            Seleccionamos el target de shapes que representar
            """
            target_shape = None
            if what == "carb":
                target_shape = self.carb_shape
            elif what == "protein":
                target_shape = self.protein_shape
            elif what == "fat":
                target_shape = self.fat_shape

            s = Shape(target_shape)
            end_min = (self._end_dt - self._start_dt).total_mins
            s.pointers(0, end_min)
            """
            Completamos cosas como el título y color
            """
            fill_color = ""
            tit = ""
            if what == "carb":
                tit = 'Carbohidratos digeridos entre\n'
                lab = 'Carbohidratos ${}g$'.format(round(s.value_inside_pointers(self.carb_total_gr), 1))
                fill_color = 'blue'
            elif what == "protein":
                tit = 'Proteinas digeridas entre\n'
                lab = 'Proteinas ${}g$'.format(round(s.value_inside_pointers(self.protein_total_gr), 1))
                fill_color = 'green'
            elif what == "fat":
                tit = 'Grasas digeridas entre\n'
                lab = 'Grasas ${}g$'.format(round(s.value_inside_pointers(self.fat_total_gr), 1))
                fill_color = 'yellow'

            tit += "{} ($0min$) y {} (${}min$)".format(self._start_dt, self._end_dt, end_min)

            ax.set_title(tit)
            ax.set_xlabel(u"Minutos relativos")
            ax.set_ylabel(u"Velocidad digestión")

            ax.xaxis.set_major_formatter(mticker.FormatStrFormatter('$%dmin$'))
            ax.yaxis.set_major_formatter(mticker.FormatStrFormatter('$%.1fg/10min$'))
            
            x_minutes = np.hsplit(np.array(target_shape), 2)[0].T[0]
            y_effect = np.hsplit(np.array(target_shape), 2)[1].T[0]
            ax.fill_between(x_minutes, y_effect, color=fill_color, alpha=0.3, label=lab)
            ax.plot(x_minutes, y_effect, color=fill_color)
            ax.axvspan(0, end_min, color='red', alpha=0.2)
            leg = mpatches.Patch(color='red', alpha=0.2, label=lab)
            ax.legend(loc='upper left', handles=[leg])

            last_offset = None
            deviation = -20
            for n, hour in enumerate(self.feeding_hours):
                offset = (hour - self._start_dt).total_mins
                text = "{}\n".format(hour.strftime('%H:%M'))
                if last_offset != None:
                    if offset - last_offset < 20:
                        deviation += 40
                
                if what == "carb":
                    text += "$+{}g$".format(self.carb_g[n])
                elif what == "protein":
                    text += "$+{}g$".format(self.protein_g[n])
                elif what == "fat":
                    text += "$+{}g$".format(self.fat_g[n])
                ax.annotate(text,
                    xy=(offset, 0),  # theta, radius
                    xytext=(offset + deviation,y_effect.min() + ((y_effect.max() - y_effect.min()) / 2.0)),    # fraction, fraction
                    textcoords='data',
                    arrowprops=dict(facecolor=fill_color, shrink=0.05),
                    horizontalalignment='left',
                    verticalalignment='bottom',
                )
                last_offset = offset
            ax.grid()
            
        return lambda ax: draw_routine(ax)
    



"""
Si hay glucosa, tirar query hacia atrás 3h, ha de encontrarse la comida, la insulina, posiblemente la actividad y otra glucosa.
La glucosa actual, y los objetos comida, insulina, actividad y la otra glucosa tienen que estar separados
por un mínimo de 1 hora.:

si no, es que se puede tratar de una glucosa de antes.
"""
def _minutes_of_difference(d1, d2):
    return abs((d1 - d2).total_seconds()) / 60.

# Trata de agrupar comidas no necesariamente tienen por qué ser usando los más
# nuevos registros. Se pueden añadir glucosas antiguas e intentará agrupar la comida
# en ese instante.


def _try_to_group_meal(glucose_level):
    context = Context(glucose_level.user_id, glucose_level.datetime)
    basic = BasicGathering(context)

    if basic.daytimes.not_ready():
        return

    # Si de verdad se trata de una glucosa después de comer, que es la que nos interesa
    # retrasando su datetime en 120 minutos nos tendría que dar la hora de la comida
    approximately_meal_datetime = glucose_level.datetime - Timedelta(minutes=120)

    if basic.daytimes.is_snack(approximately_meal_datetime):
        return

    glucose_level_before = GlucoseLevel.glucose_levels(
        user_id=context.user_id,
        from_datetime=approximately_meal_datetime - Timedelta(minutes=100),
        until_datetime=glucose_level.datetime,
        order_by_datetime=True,
        desc_order=True,
        limit=1
    )
    if glucose_level_before != None and len(glucose_level_before) > 0:
        glucose_level_before = glucose_level_before[0]
    
    feedings = Feeding.last_feedings(
            user_id=context.user_id,
            from_datetime=(approximately_meal_datetime - Timedelta(minutes=500)),
            until_datetime=glucose_level.datetime
        )
    
    # Nos quedamos con la hora de la comida
    meal_datetime = None
    diff = 0
    meal_feeding = None
    if feedings:
        for feeding in feedings:
            if not meal_feeding or _minutes_of_difference(feeding.datetime, approximately_meal_datetime) < diff:
                diff = _minutes_of_difference(feeding.datetime, approximately_meal_datetime)
                meal_feeding = feeding
        meal_datetime = meal_feeding.datetime
    else:
        return

    """
    minutos por cada actividad
    """
    intensity_minutes = {
        Activity.INTENSITY_SOFT: 0,
        Activity.INTENSITY_MEDIUM: 0,
        Activity.INTENSITY_HIGH: 0,
        Activity.INTENSITY_EXTREME: 0,
    }
    activities = Activity.activities(
        user_id=context.user_id,
        from_datetime=meal_datetime - Timedelta(minutes=10),
        until_datetime=glucose_level.datetime
    )

    for activity in activities:
        intensity_minutes[activity.intensity] += activity.minutes


    # aquí hay que sacar más de una, todas las inyectadas en ese periodo
    # y habrá que extraer lo que será absorvido de las 0h a las 3h desde la comida
    prandial_insulins = InsulinAdministration.rapid_short_insulins(
        user_id=context.user_id,
        from_datetime=approximately_meal_datetime - Timedelta(minutes=300),
        until=glucose_level.datetime
    )
    basal_insulins = InsulinAdministration.basal_insulins(
        user_id=context.user_id,
        from_datetime=approximately_meal_datetime - Timedelta(minutes=5760),
        until=glucose_level.datetime
    )

    # Si no está listo, nos vamos a tomar por culo
    if not prandial_insulins or not basal_insulins or not glucose_level_before:
        return
    
    prandial_insulins = [ShapeInsulin(insulin) for insulin in prandial_insulins]
    basal_insulins = [ShapeInsulin(insulin) for insulin in basal_insulins]

    # calculamos la insulina que absorverá el cuerpo de las 0h a las 2h desde que se coma
    prandial_insulin = 0.
    basal_insulin = 0.

    for insulin in prandial_insulins:
        value = insulin.dose_absorbed_at_range_datetime(meal_datetime, meal_datetime + Timedelta(minutes=120))
        prandial_insulin += value
    for insulin in basal_insulins:
        value = insulin.dose_absorbed_at_range_datetime(meal_datetime, meal_datetime + Timedelta(minutes=120))
        basal_insulin += value


    # Si no están lo suficientemente alejados (1h) de la glucosa actual, nos vamos
    # a tomar por culo
    if _minutes_of_difference(glucose_level.datetime, glucose_level_before.datetime) < 60. or\
        _minutes_of_difference(glucose_level.datetime, meal_datetime) < 60.:
        return

    """
    llegados aquí no queda duda, se trata de una glucosa de después de una comida.
    Extraemos todos los macronutrientes
    """
    nutrients_digested = NutrientsDigested(
        context=context,
        start_dt=meal_datetime,
        end_dt=meal_datetime + Timedelta(minutes=120)
    )
    
    # calculamos de qué comida se trata, si desayuno, comida o cena.
    meal = basic.daytimes.nearest_meal(meal_datetime)


    # Nos quedamos con el nivel de glucosa de antes añadido por el usuario
    glucose_level_before = glucose_level_before.mgdl_level

    ###
    # aquí calculamos el valor estimado que se tendrá exactamente a los 120 minutos desde la comida,
    # aunque se reciba una glucosa añadida a los 75 minutos, o a los 140 minutos, lo cuadraremos a
    # los 120 minutos.
    ###
    minutes_points = [0, 120, 180]

    # ideal
    levels_points = [glucose_level_before, GlucoseLevel.TARGET_GLUCOSE_LEVEL_120, GlucoseLevel.TARGET_GLUCOSE_LEVEL_180]

    # extraemos la función para interpolar
    interpolation = QuadraticInterpolation(minutes_points, levels_points)

    minutes_passed_from_meal = _minutes_of_difference(glucose_level.datetime, meal_datetime)

    # este sería el valor esperado en el momento en el que el usuario añadió glucosa
    expected_level = interpolation.f(minutes_passed_from_meal)
    deviation = glucose_level.mgdl_level - expected_level # desviación

    # modificamos el valor esperado a los 120 minutos con la desviación que se arrastra
    expected_level_at_120_minutes = interpolation.f(120.)
    level_at_120_minutes = expected_level_at_120_minutes + deviation

    m = GroupedMeal(
        user_id=context.user_id,
        _datetime=meal_datetime,
        meal=meal,
        carb_gr=nutrients_digested.digested_ch_gr,
        protein_gr=nutrients_digested.digested_pr_gr,
        fat_gr=nutrients_digested.digested_fa_gr,
        fiber_gr=nutrients_digested.digested_fiber,
        alcohol_gr=nutrients_digested.digested_alcohol,
        prandial_insulin=prandial_insulin,
        basal_insulin=basal_insulin,
        glucose_level_before=glucose_level_before,
        glucose_level_after=level_at_120_minutes,
        intensity_soft_minutes=intensity_minutes[Activity.INTENSITY_SOFT],
        intensity_medium_minutes=intensity_minutes[Activity.INTENSITY_MEDIUM],
        intensity_high_minutes=intensity_minutes[Activity.INTENSITY_HIGH],
        intensity_extreme_minutes=intensity_minutes[Activity.INTENSITY_EXTREME],
        
    )
    asess = analysis_session()
    asess.add(m)
    asess.commit()

    _grouped_meal_inserted(context, m)



"""
Para agrupar aperitivos
"""
def _try_to_group_snack(glucose_level):
    context = Context(glucose_level.user_id, glucose_level.datetime)
    basic = BasicGathering(context)
    
    if basic.daytimes.not_ready() or basic.daytimes.is_snack(glucose_level.datetime):
        return

    nearest_feeding = basic.daytimes.nearest_day_time(glucose_level.datetime)
    end_datetime = glucose_level.datetime
    snack_datetime = None

    if nearest_feeding == DayTimes.BREAKFAST:
        snack_datetime = end_datetime - Timedelta(minutes=9 * 60)
    else:
        snack_datetime = end_datetime - Timedelta(minutes=3 * 60)

    last_meal_datetime = snack_datetime - Timedelta(minutes=3 * 60)

    feedings = Feeding.last_feedings(
            user_id=context.user_id,
            from_datetime=last_meal_datetime - Timedelta(minutes=180),
            until_datetime=end_datetime
        )

    """
    Nos quedamos con la hora del aperitivo
    """
    dt = None
    snack_feeding = None
    if feedings:
        diff = 0
        for feeding in feedings:
            if not snack_feeding or _minutes_of_difference(feeding.datetime, snack_datetime) < diff:
                diff = _minutes_of_difference(feeding.datetime, snack_datetime)
                snack_feeding = feeding
        dt = snack_feeding.datetime

    if not dt:
        return False
    snack_datetime = dt

    """
    minutos por cada actividad
    """
    intensity_minutes = {
        Activity.INTENSITY_SOFT: 0,
        Activity.INTENSITY_MEDIUM: 0,
        Activity.INTENSITY_HIGH: 0,
        Activity.INTENSITY_EXTREME: 0,
    }
    activities = Activity.activities(
        user_id=context.user_id,
        from_datetime=snack_datetime - Timedelta(minutes=10),
        until_datetime=glucose_level.datetime
    )
    if activities:
        for activity in activities:
            intensity_minutes[activity.intensity] += activity.minutes


    """
    Insulinas
    """
    # aquí hay que sacar más de una, todas las inyectadas en ese periodo
    # y habrá que extraer lo que será absorvido desde la anterior comida hasta la siguiente
    prandial_insulins = InsulinAdministration.rapid_short_insulins(
        user_id=context.user_id,
        from_datetime=last_meal_datetime - Timedelta(minutes=300),
        until_datetime=end_datetime
    )
    
    basal_insulins = InsulinAdministration.basal_insulins(
        user_id=context.user_id,
        from_datetime=last_meal_datetime - Timedelta(days=4),
        until_datetime=end_datetime
    )

    prandial_insulins = [ShapeInsulin(insulin) for insulin in prandial_insulins]
    basal_insulins = [ShapeInsulin(insulin) for insulin in basal_insulins]

    # calculamos la insulina que absorverá el cuerpo de las 0h a las 3h desde el aperitivo, residual, del pinchazo de la comida.
    prandial_insulin = 0.
    basal_insulin = 0.

    for insulin in prandial_insulins:
        value = insulin.dose_absorbed_at_range_datetime(snack_datetime, snack_datetime + Timedelta(minutes=120))
        prandial_insulin += value
    for insulin in basal_insulins:
        value = insulin.dose_absorbed_at_range_datetime(snack_datetime, snack_datetime + Timedelta(minutes=120))
        basal_insulin += value

    """
    day_time corrrespondiente al snack
    """
    snack = basic.daytimes.nearest_snack(snack_datetime)

    """
    calculamos todos los macronutrientes que serán digeridos en el aperitivo
    """
    nutrients_digested = NutrientsDigested(
        context=context,
        start_dt=snack_datetime,
        end_dt=end_datetime
    )

    # tenemos que calcular la desviación de glucosa que se ha llevado
    # hace falta interpolar.
    last_grouped_meal = GroupedMeal.last_grouped_meals(
        user_id=context.user_id,
        from_datetime=snack_datetime - Timedelta(minutes=600),
        until_datetime=snack_datetime,
        order_by_datetime=True,
        desc_order=True,
        limit=1
    )

    if last_grouped_meal != None and len(last_grouped_meal) > 0:
        last_grouped_meal = last_grouped_meal[0]
    else:
        return

    deviation = last_grouped_meal.glucose_level_after - GlucoseLevel.TARGET_GLUCOSE_LEVEL_120
    glucose_level_before = GlucoseLevel.TARGET_GLUCOSE_LEVEL_180 + deviation
    glucose_level_after = glucose_level.mgdl_level
    
    minutes_until_next_meal = int(round((glucose_level.datetime - snack_datetime).total_seconds() / 60.))

    s = GroupedSnack(
        user_id=context.user_id,
        _datetime=snack_datetime,
        snack=snack,
        glucose_level_before=glucose_level_before,
        glucose_level_after=glucose_level_after,
        minutes_until_next_meal=minutes_until_next_meal,
        carb_gr=nutrients_digested.digested_ch_gr,
        protein_gr=nutrients_digested.digested_pr_gr,
        fat_gr=nutrients_digested.digested_fa_gr,
        fiber_gr=nutrients_digested.digested_fiber,
        alcohol_gr=nutrients_digested.digested_alcohol,
        prandial_insulin=prandial_insulin,
        basal_insulin=basal_insulin,
        intensity_soft_minutes=intensity_minutes[Activity.INTENSITY_SOFT],
        intensity_medium_minutes=intensity_minutes[Activity.INTENSITY_MEDIUM],
        intensity_high_minutes=intensity_minutes[Activity.INTENSITY_HIGH],
        intensity_extreme_minutes=intensity_minutes[Activity.INTENSITY_EXTREME],
    )
    asess = analysis_session()
    asess.add(s)
    asess.commit()

    _grouped_snack_inserted(context, s)



@on_glucose_inserted
def _glucose_inserted(glucose):
    _try_to_group_meal(glucose)
    _try_to_group_snack(glucose)




##############################################################################
"""
Esto es para aquellos submódulos que quieran ponerse a la escucha de los eventos
de añadido de comidas agrupadas o aperitivos agrupados.

@on_grouped_meal_inserted
def procesamos_comida(grouped_meal):
    pass
"""
# FOR MEALS
__grouped_meals_watchers = []
def _grouped_meal_inserted(context, target):
    for watcher in __grouped_meals_watchers:
        watcher(context, target)


"""
DECORATORS
"""
def on_grouped_meal_inserted(func): # decorator
    if func not in __grouped_meals_watchers:
        __grouped_meals_watchers.append(func)



"""
Esto es para aquellos submódulos que quieran ponerse a la escucha de los eventos
de añadido de comidas agrupadas o aperitivos agrupados.

@on_grouped_snack_inserted
def procesamos_aperitivo(grouped_snack):
    pass
"""
# FOR SNACKS
__grouped_snacks_watchers = []

def _grouped_snack_inserted(context, target):
    for watcher in __grouped_snacks_watchers:
        watcher(context, target)

"""
DECORATOR
"""
def on_grouped_snack_inserted(func): # decorator
    if func not in __grouped_snacks_watchers:
        __grouped_snacks_watchers.append(func)


def main():
    context = Context(1, Datetime(2017, 1, 1, 13, 0))
    
    nutrients_digested = NutrientsDigested(
        context=context,
        start_dt=Datetime(2017, 1, 1, 13, 0),
        end_dt=Datetime(2017, 1, 1, 15, 0)
    )
    nutrients_digested.plt_show()
    
    import sys
    sys.exit()


if __name__ == "__main__":
    main()

