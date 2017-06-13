# -*- coding: utf-8 -*-

from dia.predictive.interfaces import AbstractPredictiveSystem
from dia.interfaces import DescriptiveRepositoryAdapter

import settings


"""
This is the facade of the application

It needs a AbstractDescriptiveRepository implementation and at least one
AbstractPredictiveSystem implementation to work.
"""
class DiaCore(DescriptiveRepositoryAdapter):
    """
    From DescriptiveRepositoryAdapter inherits the following methods:

    def add_glucose_level(self, glucose):
    def add_activity(self, activity):
    def add_feeding(self, feeding):
    def add_insulin_administration(self, insulin):
    def update_trait(self, trait):

    For querys, not all parameters are mandatory
    def get_glucoses(self, user_pk, from_utc_timestamp=None, until_utc_timestamp=None, mgdl_level_above=None, mgdl_level_below=None, limit=None, order_by_utc_timestamp=True, order_ascending=True):
    def get_activities(self, user_pk, from_utc_timestamp=None, until_utc_timestamp=None, limit=None, order_by_utc_timestamp=True, order_ascending=True):
    def get_traits(self, user_pk, trait, from_utc_timestamp=None, until_utc_timestamp=None, limit=None, order_by_utc_timestamp=True, order_ascending=True):
    def get_feedings(self, user_pk, from_utc_timestamp=None, until_utc_timestamp=None, limit=None, order_by_utc_timestamp=True, order_ascending=True):
    def get_insulin_administrations(self, user_pk=None, from_utc_timestamp=None, until_utc_timestamp=None, limit=None, order_by_utc_timestamp=True, order_ascending=True):

    def add_descriptive_observer(self, obs):
    """
    def __init__(self, descriptive_repository_class=None):
        super(DiaCore, self).__init__(repository=descriptive_repository_class())

        # list of predictive systems to use
        self._predictive_systems = []

    
    def add_predictive_system(self, system):
        assert isinstance(system, AbstractPredictiveSystem),\
            "Invalid AbstractPredictiveSystem provided"

        assert system.unique_identificator not in \
            [s.unique_identificator for s in self._predictive_systems],\
            "unique_identificator of system provided is not unique"

        if system in self._predictive_systems:
            return

        # lo aniadimos
        self._predictive_systems.append(system)

        # lo aniadimos como observer
        self.add_descriptive_observer(system)

        # de esta forma todos seran notificados por si necesitan realizar
        # calculos. Despues, solo a uno se le podra consultar por recomendacion.

        # El unique_identificator de cada sistema predictivo podria
        # asociarse a cada usuario que utilice dia.


    # Se pedira recomendacion solo a un sistema predictivo.
    def get_recommendation(self, user_pk=None, utc_timestamp=None, predictive_system_unique_identificator=None):
        assert len(self._predictive_systems) > 0, "There is no predictive systems added"

        ui = predictive_system_unique_identificator
        assert ui in [system.unique_identificator for system in self._predictive_systems],\
            "There is no predictive system called {}".format(ui)

        for system in self._predictive_systems:
            if system.unique_identificator == ui:
                return system.get_recommendation(user_pk, utc_timestamp)
        """
        For the response returned see dia.interfaces.predictive
        """


"""
diacore element is the entry point and can be retrieved as needed
"""
diacore = DiaCore(settings.DESCRIPTIVE_REPOSITORY())

for System in settings.PREDICTIVE_SYSTEMS:
    diacore.add_predictive_system(System())

