# -*- coding: utf-8 -*-
from ..basics.context import Context


class CalculationCache(object):
    """
    _calculation_results_cached almacenará en una lista los objetos
    Context() con parametros adicionales resultados del calculado de rutinas
    especificadas por:
    
    _calculation_routines: lista con rutinas que aceptarán un parámetro Context()
    y que devolverán un diccionario key / value con los resultados de los cálculos.
    
    Cada uno de los keys serán añadidos como atributos a los contexts de la lista anterior y estos
    serán actualizados en caso de que existan o bien añadidos como nuevos
    
    El orden de ejecución de las rutinas de cálculo será el mismo que se usó al irlas
    añadiendo. Al encontrarse una que no devuelva None se interrumpirá la ejecución de las
    siguientes rutinas.
    
    Para retornar algún parámetro concreto tendrá que usarse el método get_calculated_parameter(context, parameter)
    """
    _calculation_results_cached = []
    _calculation_routines = []
    _calculation_valid_from_n_hours = -1
    _calculation_valid_until_n_hours = 1
    _calculation_valid_from_n_hours_provided = -1
    _calculation_valid_until_n_hours_provided = 1
    

    # por defecto los datos expiran a la hora
    def __init__(self, **kvargs):
        self._calculation_results_cached = []
        self._calculation_routines = []

        if "valid_from" in kvargs:
            self._calculation_valid_from_n_hours_provided = kvargs['valid_from']
        else:
            self._calculation_valid_from_n_hours_provided = -1

        if "valid_until" in kvargs:
            self._calculation_valid_until_n_hours_provided = kvargs['valid_until']
        else:
            self._calculation_valid_until_n_hours_provided = 1
            
        if self._calculation_valid_from_n_hours > self._calculation_valid_until_n_hours:
            self._calculation_valid_from_n_hours_provided = -1
            self._calculation_valid_until_n_hours_provided = 1
        
        if "routines" in kvargs:
            self.add_routines(kvargs['routines'])

  
    def _remove_user_id(self, user_id):
        self._calculation_results_cached = [x for x in self._calculation_results_cached if x.user_id != user_id]
    
    def _update_context_element(self, context):
        self._remove_user_id(context.user_id)
        self._calculation_results_cached.append(context)
    
   
    def _get_calculation(self, context):
        result = None
        for c in self._calculation_results_cached:
            if c.user_id == context.user_id:
                result = c
        
        valid_calculation = True
        
        if result == None:
            valid_calculation = False
        else:
            seconds_diff = (context.current_datetime - result.current_datetime).total_seconds()
            hours_diff = seconds_diff / 60. / 60.
            if hours_diff < result.valid_from or \
                hours_diff > result.valid_until:
                valid_calculation = False

        if not valid_calculation:        
            result = Context(context.user_id, context.current_datetime)
            result.valid_from = -1
            result.valid_until = 1
            """
            Si el cálculo no está realizado, configuramos temporalmente
            que se compruebe desde hace una hora hasta una hora por delante
            
            Si se encuentra algún cálculo, el desde y el hasta se volverán
            a configurar con los valores provistos desde el constructor.
            """
            
            for rutine in self._calculation_routines:
                kv = rutine(context)
                if kv != None:
                    for key in kv:
                        setattr(result, key, kv[key])

                    result.valid_from = self._calculation_valid_from_n_hours_provided
                    result.valid_until = self._calculation_valid_until_n_hours_provided
                    break
            self._update_context_element(result)

        return result
    
    def add_routine(self, routine):
        if routine not in self._calculation_routines: 
            self._calculation_routines.append(routine)

    def add_routines(self, routines):
        for routine in routines:
            if routine not in self._calculation_routines: 
                self._calculation_routines.append(routine)
    
    def get_calculated_parameter(self, context, parameter):
        calculation_result = self._get_calculation(context)
        return getattr(calculation_result, parameter, None)




