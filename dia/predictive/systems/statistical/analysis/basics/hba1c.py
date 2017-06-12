# -*- coding: utf-8 -*-


import matplotlib.patches as mpatches
import matplotlib.ticker as mticker
import numpy as np
import math

from ...analysis.tools.stats import PolynomialRegression, LinearRegression


# MODELOS
################################################################################
from ...analysis.model import engine as predictive_engine
from ...analysis.model import analysis_session


from sqlalchemy import Column, Integer, Float, Date
from sqlalchemy.ext.declarative import declarative_base
from dia.predictive.systems.statistical.analysis.tools.graphs import Graph
from dia.predictive.systems.statistical.analysis.tools.property import propertycached
from dia.predictive.systems.statistical.analysis.basics.context import Context
from dia.predictive.systems.statistical.analysis.basics.daytimes import DayTimes
from dia.predictive.systems.statistical.tools.dates import Datetime, Timedelta


Base = declarative_base(predictive_engine)

class _HbA1cRecord(Base):
    """"""
    __tablename__ = 'analysis_basics_hba1c_records'

    """"""
    id = Column(Integer, primary_key=True)  # lint:ok
    user_id = Column(Integer, nullable=False, index=True)
    date = Column(Date, nullable=False, index=True)

    # recommended doses absorved in 24 hours
    value = Column(Float, nullable=False)
    
    def __str__(self):
        st = "HbA1cRecord: user_id: {}, date: {}, value: {}".format(
            self.user_id,
            self.date,
            self.value
        )
        return st
    
    @staticmethod
    def last_values(**kvargs):
        options = {
                'user_id': None,
                'from_date': None,
                'until_date': None,
                'order_by_date': True,
                'desc_order': False,
                'limit': None }
    
        options.update(kvargs)
        
        if options['user_id'] == None:
            return None

        se = analysis_session()
        r_query = se.query(_HbA1cRecord).\
            filter(_HbA1cRecord.user_id == options['user_id'])


        """
        Dates
        """
        if options['until_date'] != None:        
            r_query = r_query.filter(_HbA1cRecord.date <= options['until_date'])
        
        if options['from_date'] != None:        
            r_query = r_query.filter(_HbA1cRecord.date >= options['from_date'])
        

        """
        Order
        """
        if options['order_by_date']:
            if options['desc_order']:
                r_query = r_query.order_by(_HbA1cRecord.date.desc())
            else:
                r_query = r_query.order_by(_HbA1cRecord.date)

        """
        Limit
        """
        if options['limit'] != None:     
            r_query = r_query.limit(options['limit'])
        
        return r_query.all()
    
    @staticmethod
    def update_value(user_id, date, value):
        se = analysis_session()
        last = se.query(_HbA1cRecord).\
            filter(_HbA1cRecord.user_id == user_id).\
            filter(_HbA1cRecord.date == date).\
            first()

        if last == None:
            record = _HbA1cRecord(
                user_id=user_id,
                date=date,
                value=value
            )
            se.add(record)
        else:
            last.value = value
        
        se.commit()
            

Base.metadata.create_all(checkfirst=True)

# Fin de los modelos
##########################################################################



class _HbA1cGraph(Graph):
    def __init__(self, parent, current_value):
        options = {
            "name": 'HbA1c',
            "figsize": (8, 6),
#            "dpi": 70,
            "cols": 1,
        }
        super(_HbA1cGraph, self).__init__(**options)
        self.parent = parent
        self.add_drawing_routine(self._drawing_routine())
        
    def _drawing_routine(self):

        def draw_routine(ax):
            x_days_old = self.parent.records_days_passed
            y_values = self.parent.records_values

            """
            Completamos cosas como el título y color
            """
            GREEN_ZONE = [4., 6.2]
            ORANGE_ZONE = [6.2, 7.5]
            RED_ZONE = [7.5, 10.]
            
            if len(y_values) > 0:
                min_value = np.min(y_values)
                max_value = np.max(y_values)
                
                min_value -= 0.5
                max_value += 0.5
    
                if min_value > RED_ZONE[0]:
                    GREEN_ZONE = None
                    ORANGE_ZONE = None
                    RED_ZONE[0] = min_value
                elif min_value > ORANGE_ZONE[0]:
                    GREEN_ZONE = None
                    ORANGE_ZONE[0] = min_value
                elif min_value > GREEN_ZONE[0]:
                    GREEN_ZONE[0] = min_value
                
                if max_value < GREEN_ZONE[1]:
                    RED_ZONE = None
                    ORANGE_ZONE = None
                    GREEN_ZONE[1] = max_value
                elif max_value < ORANGE_ZONE[1]:
                    RED_ZONE = None
                    ORANGE_ZONE[1] = max_value
                else:
                    RED_ZONE[1] = max_value

                ax.set_ylim(min_value, max_value)
                ax.set_xlim(np.min(x_days_old), np.max(x_days_old) + 1)

            
            ax.set_title("Hemoglobina glicosilada")
            ax.set_xlabel(u"Días de antigüedad")
            ax.set_ylabel(u"% Hemoglobina glicosilada")
            

            ax.xaxis.set_major_formatter(mticker.FormatStrFormatter('$%d$'))
            ax.yaxis.set_major_formatter(mticker.FormatStrFormatter('$%.1f$%%'))
            
            ax.scatter(x_days_old, y_values, marker='*', color='blue', alpha=0.3)

            """
            Linear regression
            """
            linear_x, linear_y = self.parent.linear_regression.data_to_plot(np.min(x_days_old), np.max(x_days_old) + 1)
            regression, = ax.plot(linear_x, linear_y, color='red', label=u"$f(x)={}$".format(self.parent.linear_regression.latex))
            
        
            """
            Polynomial regression
            """
            poly_x, poly_y = self.parent.polynomial_regression.data_to_plot(np.min(x_days_old), np.max(x_days_old) + 1)
            poly_tex = self.parent.polynomial_regression.latex
            poly_regression, = ax.plot(poly_x, poly_y, label=r"$g(x)={}$".format(poly_tex))
            

            """
            Zonas
            """            
            if GREEN_ZONE != None:            
                ax.axhspan(GREEN_ZONE[0], GREEN_ZONE[1], color='green', alpha=0.05)
            if ORANGE_ZONE != None:
                ax.axhspan(ORANGE_ZONE[0], ORANGE_ZONE[1], color='orange', alpha=0.1)
            if RED_ZONE != None:
                ax.axhspan(RED_ZONE[0], RED_ZONE[1], color='red', alpha=0.1)
            
            ax.axvspan(0, 0, color='black')
            ax.annotate("{}: HbA1c ${}$%".format(self.parent.context.current_datetime.date(), round(self.parent.current_value, 1)),
                xy=(0, self.parent.current_value),  # theta, radius
                xytext=(-2, ((self.parent.current_value - min_value) / 2.0) + min_value),    # fraction, fraction
                textcoords='data',
                arrowprops=dict(facecolor='black', shrink=0.05),
                horizontalalignment='right',
                verticalalignment='bottom',
            )
            

            leg = mpatches.Patch(alpha=0., label="HbA1c actual: ${}$%".format(round(self.parent.current_value, 1)))
            future_leg = None
            if self.parent.linear_regression.f != None:
                future_leg = mpatches.Patch(alpha=0., label=u"Estimación 30 días: ${}$%".format(round(self.parent.future_value(30), 1)))
            
            if regression != None and future_leg != None:
                ax.legend(loc='upper left', handles=[leg, future_leg, regression, poly_regression,])
            else:
                ax.legend(loc='upper left', handles=[leg])
            ax.grid()
            
        return lambda ax: draw_routine(ax)
    

class HbA1c(object):
    """
    Se tiene que ocupar de dos cosas:
    1.- Realizar una serie de cálculos con las últimas entradas de valores HbA1c,
        regresión lineal, valor actual, etc.
    2.- Facilitar el añadido de nuevas entradas para valores de HbA1c
    """
    
    def __init__(self, context):
        self._c = context
        self.records = _HbA1cRecord.last_values(
            user_id=self._c.user_id,
            until_date=self._c.current_datetime.date(),
            order_by_date=True,
            desc_order=True,
            limit=120
        )
        if self.records == None:
            self.records = []
        
        if len(self.records) > 0:
            self.linear_regression = LinearRegression(self.records_days_passed, self.records_values)
        
            degree = len(self.records)
            if degree > 3: degree = 3

            self.polynomial_regression = PolynomialRegression(self.records_days_passed, self.records_values, degree)
            self.graph = _HbA1cGraph(self, self.current_value)
    
    @property
    def context(self):
        return self._c
    
    
    def __str__(self):
        str = """HbA1c:
Current value ................. {}%
Estimated value in 30 days .... {}%
Estimated value in 60 days .... {}%
Estimated value in 90 days .... {}%""".format(
        self.current_value,
        self.future_value(30),
        self.future_value(60),
        self.future_value(90))
        return str
    

    @propertycached
    def records_days_passed(self):
        list_ = [(record.date - self._c.current_datetime.date()).total_seconds() / 60. / 60. / 24. for record in self.records]
        return list_
    
    @propertycached
    def records_values(self):
        list_ = [record.value for record in self.records]
        return list_
    
    

    
    """
    Valor actual
    """
    @propertycached
    def current_value(self):
        if len(self.records) > 0:
            return self.records[0].value
        return 0.0
    
    """
    Valor futuro
    .future_value(30) devolvería el % estimado en 30 días.
    """
    def future_value(self, days):
        f = self.linear_regression.f
        return f(days)
    
    
    @staticmethod
    def _weight(days_old):
        assert days_old >= 0, "days_old debe ser mayor o igual a 0"
        return 1.0 / (math.pow(2, (days_old / 30.0)))
    

    @staticmethod
    def _mgdl2hba1cpercentage(mgdl):
        return ((mgdl - 60.) / 31.) + 4.
    

    """
    Recalcula el HbA1c para el start_dt especificado.
    Si existe un record lo actualiza, si no, añade una nueva entrada
    """
    def recalculate(self, day_times):
        options = {
                'user_id': self._c.user_id,
                'from_datetime': self._c.current_datetime - Timedelta(days=120),
                'until_datetime': self._c.current_datetime,
                'order_by_datetime': True,
                'desc_order': False,
        }
        glucoses = GlucoseLevel.glucose_levels(**options)
        
        if glucoses == None:
            glucoses = []

        value = 0.
        total = 0.
        n = 0.

        last_days_old = None
        meals_day_times = []
        snacks_day_times = []
        
        for glucose in glucoses:
            day_time = day_times.nearest_day_time(glucose.datetime)
            days_old = (self._c.current_datetime - glucose.datetime).total_days
            
            if last_days_old == None: last_days_old = days_old
            
            if last_days_old != days_old:
                if len(snacks_day_times) < len(meals_day_times):
                    number = len(meals_day_times) - len(snacks_day_times)
                    for _ in range(number):
                        total += 150. * HbA1c._weight(last_days_old)
                        n += HbA1c._weight(last_days_old)

                last_days_old = days_old
                meals_day_times = []
                snacks_day_times = []
            
            if day_times.is_meal(glucose.datetime):
                meals_day_times.append(day_time)
            else:
                snacks_day_times.append(day_time)
            
            total += glucose.mgdl_level * HbA1c._weight(days_old)
            n += HbA1c._weight(days_old)
        
        if n > 0.:
            value = HbA1c._mgdl2hba1cpercentage(total / n)
            _HbA1cRecord.update_value(self._c.user_id, self._c.current_datetime.date(), value)



def _recalculate_hba1c(glucose):
    context = Context(glucose.user_id, glucose.datetime)

    day_times = DayTimes(context)
    hba1c = HbA1c(context)

    hba1c.recalculate(day_times)
            
        
        
def main():
    context = Context(1, Datetime(2017, 1, 12, 13, 0))

    h = HbA1c(context)
    h.graph.show()
    
    
    import sys
    sys.exit()


if __name__ == "__main__":
    main()


    
    
