# -*- coding: utf-8 -*-
"""
Aquí nos limitamos a reflejar la realidad del diabético relativa
a las cantidades de insulina basal que se está administrando
así como el patrón de insulinas que usa.

Expone varias funciones para hacer fácil recoger estos datos.
"""
from modules.analysis.basics.daytimes import DayTimes

import logging

# MODELOS
################################################################################
from modules.analysis.model import engine as predictive_engine
from modules.analysis.model import analysis_session
from sqlalchemy import Column, Integer, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from modules.descriptive.models import InsulinAdministration
from modules.analysis.tools.property import propertycached
from modules.tools.dates import Timedelta
from modules.descriptive.events import on_insulin_inserted
from modules.analysis.tools.context import Context

Base = declarative_base(predictive_engine)

class _BasalInsulin24hDoses(Base):
    """"""
    __tablename__ = 'analysis_basics_basal_doses_24h'

    """"""
    id = Column(Integer, primary_key=True)  # lint:ok
    user_id = Column(Integer, nullable=False)
    datetime = Column(DateTime, nullable=False, index=True)

    # recommended doses absorved in 24 hours
    doses_absorved_24h = Column(Float, nullable=False)
    
    def __str__(self):
        st = "BasalInsulinNeeds: user_id: {}, datetime: {}, doses_absorved_24h: {}".format(
            self.user_id,
            self.datetime,
            self.doses_absorved_24h
        )
        return st
    
    @staticmethod
    def most_recent_record(context):
        s = analysis_session()
        record = s.query(_BasalInsulin24hDoses).\
            filter(_BasalInsulin24hDoses.user_id == context.user_id).\
            filter(_BasalInsulin24hDoses.datetime <= context.current_datetime).\
            order_by(_BasalInsulin24hDoses.datetime.desc()).\
            first()
        s.close()
        return record
        


class _BasalInsulinPattern(Base):
    """
    Cada vez que una dosis basal inyectada por el usuario cambia de zona del dia,
    cambia el tipo inyectado, no correspondiente a lo que normalmente se usa,
    o cambia la dosis del tipo que acostumbra a inyectarse, se añade una nueva entrada
    aquí.
    """
    """"""
    __tablename__ = 'analysis_basics_basal_patterns'

    """"""
    id = Column(Integer, primary_key=True)  # lint:ok
    user_id = Column(Integer, nullable=False)
    datetime = Column(DateTime, nullable=False, index=True)

    day_time = Column(Integer, nullable=False)
    type = Column(Integer, nullable=False)
    proportion = Column(Float, nullable=False) # la proporción usando rounded(proportion, 1) (con un decimal.)

    def __str__(self):
        st = "BasalInsulinPattern: user_id: {}, datetime: {}, day_time: {}, type: {}, proportion: {}".format(
            self.user_id,
            self.datetime,
            self.day_time,
            self.type,
            self.proportion,
        )
        return st

    @staticmethod
    def most_recent_record(context):
        s = analysis_session()
        record = s.query(_BasalInsulinPattern).\
            filter(_BasalInsulinPattern.user_id == context.user_id).\
            filter(_BasalInsulinPattern.datetime < context.current_datetime).\
            order_by(_BasalInsulinPattern.datetime.desc()).\
            first()
        s.close()
        return record

    @staticmethod
    def records_at_datetime(context, dt):
        s = analysis_session()
        records = s.query(_BasalInsulinPattern).\
            filter(_BasalInsulinPattern.user_id == context.user_id).\
            filter(_BasalInsulinPattern.datetime == dt).\
            order_by(_BasalInsulinPattern.datetime.desc()).\
            all()
        s.close()
        return records


Base.metadata.create_all(checkfirst=True)

# Fin de los modelos
##########################################################################


class BasalInsulin(object):
    """
    basal = BasalInsulin(context, day_times)
    basal.last_basal_change ==> ultimo cambio en basal
    basal.insulin_pattern ==> patron de insulina
    basal.doses_24h ==> dosis totales en 24h que actualmente se administra
    basal.when ==> devolviese los day_times donde hay que pincharse
    basal.what_type(day_time) ==> tipo usado en el day time
    basal.what_proportion(day_time) ==> proporción que usar como factor para doses_24h
    basal.injections ==> inyecciones por día
    """

    def __init__(self, context, day_times):
        assert isinstance(day_times, DayTimes), "day_times debe ser una instancia de modules.analysis.basics.daytimes.DayTimes"
        assert not day_times.not_ready(), "day_times aún no está listo. ¿No se añadieron las insulinas usadas en la db aún?"
        
        self._c = context
        
        self.day_times = day_times
    
    def __str__(self):
        s = """BasalInsulin:
last_basal_change: ......... {}
doses in 24 hours .......... {}
number of injections ....... {}
day_times with injection ... {}
""".format(
            self.last_basal_change,
            self.doses_24h,
            self.injections,
            self.when()
        )
        for day_time in self.when():
            s += "in day_time {} type {} proportion {}\n".format(day_time, self.what_type(day_time), self.what_proportion(day_time))
        return s

    @property
    def user_id(self):
        return self._c.user_id

    @property
    def current_datetime(self):
        return self._c.current_datetime

    @property
    def _insulins(self):
        """
        metodo preferido
        """
        insulins = InsulinAdministration.basal_insulins(
            user_id=self._c.user_id,
            from_datetime=self.last_basal_change + Timedelta(days=1),
            until_datetime=self._c.current_datetime,
            order_by_datetime=True,
            desc_order=True,
            limit=30
        )
        
        if insulins != None and len(insulins) > 0:
            return insulins

        """
        Metodo alternativo
        """
        insulins = InsulinAdministration.basal_insulins(
            user_id=self._c.user_id,
            until_datetime=self._c.current_datetime,
            order_by_datetime=True,
            desc_order=True,
            limit=30
        )
        
        if insulins != None and len(insulins) > 0:
            return insulins
        
        return []
    
    @propertycached
    def last_basal_change(self):
        current_module = __name__.split('.')[-1]
        log = logging.getLogger(current_module + " >") 
        
        dt = None
    
        last_basal_pattern_record = _BasalInsulinPattern.most_recent_record(self._c)
        last_insulin_24h_doses_record = _BasalInsulin24hDoses.most_recent_record(self._c)
        if last_basal_pattern_record == None and last_insulin_24h_doses_record == None:
            dt = self._c.current_datetime - Timedelta(days=30)
        elif last_basal_pattern_record != None and last_insulin_24h_doses_record == None:
            dt = last_basal_pattern_record.datetime
        elif last_basal_pattern_record == None and last_insulin_24h_doses_record != None:
            dt = last_insulin_24h_doses_record.datetime
        else:
            if (self._c.current_datetime - last_basal_pattern_record.datetime) < (self._c.current_datetime - last_insulin_24h_doses_record.datetime):
                dt = last_insulin_24h_doses_record.datetime
            else:
                dt = last_basal_pattern_record.datetime
        
        #log.info("Como last basal change calculamos la fecha: {}".format(dt))
        return dt
    
    def when(self):
        result = []
        if self.insulin_pattern != None:
            result = [day_time for day_time in self.insulin_pattern if day_time in DayTimes.ALL_DAY_TIMES]
        return result
    
    def what_type(self, day_time):
        assert day_time in DayTimes.ALL_DAY_TIMES, "day_time no está dentro de {}".format(DayTimes.ALL_DAY_TIMES)
        assert self.insulin_pattern != None, "patron de insulinas aún no calculado"

        if day_time in self.insulin_pattern:
            return self.insulin_pattern[day_time]["type"]

        return None
    
    def what_proportion(self, day_time):
        assert day_time in DayTimes.ALL_DAY_TIMES, "day_time no está dentro de {}".format(DayTimes.ALL_DAY_TIMES)
        assert self.insulin_pattern != None, "patron de insulinas aún no calculado"

        if day_time in self.insulin_pattern:
            return self.insulin_pattern[day_time]["proportion"]

        return None
    
    @property
    def injections(self):
        assert self.insulin_pattern != None, "patron de insulinas aún no calculado"
        return self.insulin_pattern["injections_per_day"]

    @propertycached
    def insulin_pattern(self):
        assert not self.day_times.not_ready(), "day_times no está preparado aún"
        
        last_result = {}
        most_recent_pattern_record = _BasalInsulinPattern.most_recent_record(self._c)
        most_recent_pattern_datetime = None
        if most_recent_pattern_record != None:
            most_recent_pattern_datetime = most_recent_pattern_record.datetime
            patterns = _BasalInsulinPattern.records_at_datetime(self._c, most_recent_pattern_datetime)
            if patterns != None and len(patterns) > 0:
                for pattern in patterns:
                    last_result[pattern.day_time] = {}
                    last_result[pattern.day_time]['proportion'] = pattern.proportion
                    last_result[pattern.day_time]['type'] = pattern.type
                last_result['injections_per_day'] = len(patterns)

        result = {}
        for day_time in DayTimes.ALL_DAY_TIMES:
            result[day_time] = {} 
            result[day_time]['number_of_ocurrences'] = 0.
            result[day_time]['total_doses'] = 0.
            result[day_time]['types_encountered'] = []
            result[day_time]['mean_dose'] = 0.
            result[day_time]['proportion'] = 0.
            result[day_time]['type'] = 0.
    
        total_ocurrences = 0.
        for insulin in self._insulins:
            day_time = self.day_times.nearest_day_time(insulin.datetime)
            total_ocurrences += 1.
            result[day_time]['number_of_ocurrences'] += 1
            result[day_time]['total_doses'] += insulin.dose
            result[day_time]['types_encountered'].append(insulin.type)
    
        if total_ocurrences == 0.:
            return None
        """
        Primero nos quedamos con aquellos day times en los que el número
        de ocurrencias haya superado el 20%
        """
        day_times_with_basal_injections = []
        for day_time in DayTimes.ALL_DAY_TIMES:
            percent = (result[day_time]['number_of_ocurrences'] / total_ocurrences) * 100
            if percent > 20.:
                day_times_with_basal_injections.append(day_time)
        
        """
        Nos guardamos el número de inyecciones por día
        """
        result['injections_per_day'] = len(day_times_with_basal_injections)
        
    
        """
        El siguiente paso es conseguir la dosis media aplicada en cada day_time
        """
        total_doses = 0.
        for day_time in day_times_with_basal_injections:
            day_time_mean_dose = result[day_time]['total_doses'] / result[day_time]['number_of_ocurrences']
            total_doses += day_time_mean_dose
        
        for day_time in day_times_with_basal_injections:
            day_time_mean_dose = result[day_time]['total_doses'] / result[day_time]['number_of_ocurrences']
            result[day_time]['proportion'] = day_time_mean_dose / total_doses
    
            types_count = {}
            for insulin_type in result[day_time]['types_encountered']:
                if insulin_type not in types_count:
                    types_count[insulin_type] = 0
                types_count[insulin_type] += 1
            
            """
            Nos quedamos en el day_time con el tipo de insulina basal más repetido
            """
            result[day_time]['type'] = max(types_count.iterkeys(), key=(lambda key: types_count[key]))
            
        
        """
        Y llegados a este punto tenemos que eliminar del diccionario resultado
        todas las claves que no sirvan y devolverlo
        """
        for day_time in DayTimes.ALL_DAY_TIMES:
            if day_time not in day_times_with_basal_injections:
                del result[day_time]
            else:
                del result[day_time]['number_of_ocurrences']
                del result[day_time]['total_doses']
                del result[day_time]['types_encountered']
                del result[day_time]['mean_dose']
    
    
        """
        result[day_times]['type']
        result[day_times]['proportion']
        result['injections_per_day']
        
        
        Hay que comprobar si los patrones de insulina actuales son los guardados en la db,
        si en la bd no hubiese datos, o si hubiesen cambiado, hay que guardar el nuevo patron de
        insulinas e intentar hacer la recomendación, pero sin modificar lo que el usuario
        se viene pinchando, al no tener aún datos de glucosas que analizar
        """
        pattern_changed = False
        
        if last_result != {}:
            for day_time in last_result:
                if day_time not in DayTimes.ALL_DAY_TIMES:
                    continue
                if day_time not in result:
                    pattern_changed = True
                elif result[day_time]['proportion'] != last_result[day_time]['proportion']:
                    pattern_changed = True
                if pattern_changed:
                    break 
        else:
            pattern_changed = True
    
        if pattern_changed:
            """
            Hay que guardar el nuevo patron de insulinas
            """
            s = analysis_session()
            for day_time in result:
                if day_time not in DayTimes.ALL_DAY_TIMES:
                    continue

                pattern = _BasalInsulinPattern(
                    user_id=self._c.user_id,
                    datetime=self._c.current_datetime,
                    day_time=day_time,
                    type=result[day_time]['type'],
                    proportion=result[day_time]['proportion']
                )
                s.add(pattern)
            s.commit()
    
    
        """
        Nos queda sólo:
        result[day_time]['proportion']
        result[day_time]['type']
        result['injections_per_day']
        """
        return result

    @propertycached
    def doses_24h(self):
        
        """
        self._insulins está ordenado de más actual a menos actual
        
        Tenemos que coger un día en el que se estén administrando los pinchazos por día
        que se suelen hacer, cuyo día anterior también los tenga y el anterior del 
        anterior también.
        
        Tres días consecutivos en los que el número de pimchazos que se deberían aplicar
        se hayan aplicado
        """
        pattern = self.insulin_pattern
        """
        Si esto no se cumple retornamos None
        """
        if pattern == None or len(self._insulins) == 0:
            return None


        """
        Para comparar recogemos el último dato guardado
        """        
        last_24h_doses = None
        last_24h_doses_record = _BasalInsulin24hDoses.most_recent_record(self._c)
        
        if last_24h_doses_record != None:
            last_24h_doses = last_24h_doses_record.doses_absorved_24h

        """
        Comenzamos el cálculo
        """
        current_24h_doses = None
        injections = pattern['injections_per_day']
        
        last_day = 0
        insulins_selected = []
        temp_insulins_selected = []

        for insulin in self._insulins:
            if last_day == 0: last_day = insulin.datetime.day
            
            if insulin.datetime.day != last_day:
                last_day = insulin.datetime.day
                
                """
                Si el número de insulinas administradas temporalmente recogidas
                coincide con el número de pinchazos que hay que hacer al día las añadimos a la lista definitiva
                """
                if len(temp_insulins_selected) == injections:
                    insulins_selected += temp_insulins_selected
                    
                    """
                    Si la lista definitiva tiene 3 días de insulinas en rango, rompemos el bucle
                    """
                    if len(insulins_selected) > 0 and \
                    round(abs((insulins_selected[0].datetime - insulins_selected[-1].datetime).total_seconds())/60./60./24.) >= 3:
                        break
                else:
                    """
                    Si el día cambió y las insulinas temporales no coinciden con el número de pinchazos
                    al día, eliminamos la lista definitiva. Necesitamos tres días completos
                    """
                    insulins_selected = []

                """
                Reinicializamos la lista temporal de insulinas elegidas
                """
                temp_insulins_selected = []

            """
            Añadimos a la lista temporal la insulina actual
            """                
            temp_insulins_selected.append(insulin)
    
        if len(temp_insulins_selected) == injections:
            insulins_selected += temp_insulins_selected

        if len(insulins_selected) > 0:
            total = 0.
            for insulin in insulins_selected:
                total += insulin.dose
            
            total /= len(insulins_selected)
            total *= injections
            
            if total > 0.:
                current_24h_doses = total
        else:
            """
            Algoritmo alternativo
            """
            if self._insulins != None:
                n = 0.
                total_doses = 0.
            
                last_day = 0.
                for insulin in self._insulins:
                    if last_day == 0: last_day = insulin.datetime.day
                    
                    if insulin.datetime.day != last_day:
                        last_day = insulin.datetime.day
                        n += 1
                        
                    total_doses += insulin.dose
            
                if len(self._insulins) > 0:
                    n += 1        
            
                if n > 2:
                    current_24h_doses = round(total_doses / n)
        
        
        if current_24h_doses != None:
            if last_24h_doses == None or current_24h_doses != last_24h_doses:
                """
                Tenemos que guardar una nueva entrada
                """
                basal_doses = _BasalInsulin24hDoses(
                    user_id=self._c.user_id,
                    datetime=self._c.current_datetime,
                    doses_absorved_24h=current_24h_doses
                )
                s = analysis_session()
                s.add(basal_doses)
                s.commit()
        elif last_24h_doses != None:
                return last_24h_doses
        
        return current_24h_doses


"""
Se hacen dos cosas:
Se recupera el último registro guardado.
Se intenta calcular con lo encontrado en días completos

Si no existiese el último registro guardado, con que haya 1 día completo, lo guardamos
Si sí existe, tendrá que haber dos días completos y no corresponderse el nuevo cálculo con
el guardado, y guardarlo.
"""
@on_insulin_inserted
def _basal_checks(insulin):
    context = Context(insulin.user_id, insulin.datetime)
    day_times = DayTimes(context)
    if day_times.is_ready():
        basal = BasalInsulin(context, day_times)
        pattern = basal.insulin_pattern
        dose_24h = basal.doses_24h
        """
        Esto es una mierda cutre pero debería bastar para guardar en la database
        los cambios que vayan surgiendo con el patrón de insulinas o las dosis
        en 24 horas administradas.
        """
        

