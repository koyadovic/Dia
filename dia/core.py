# -*- coding: utf-8 -*-

from dia.interfaces import DescriptiveRepositoryAdapter, AbstractPredictiveSystem, RecommendationResponse,\
    PredictiveRequestContext

from . import settings
from dia.models import GlucoseLevel, Activity, Feeding, InsulinAdministration,\
    Trait, Configuration, ConfigurationKey
from dia.time import Timestamp


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
    def update_configuration(self, config):

    For querys, not all parameters are mandatory
    def get_glucoses(self, user_pk, from_timestamp=None, until_timestamp=None, mgdl_level_above=None, mgdl_level_below=None, limit=None, order_by_timestamp=True, order_ascending=True):
    def get_activities(self, user_pk, from_timestamp=None, until_timestamp=None, limit=None, order_by_timestamp=True, order_ascending=True):
    def get_feedings(self, user_pk, from_timestamp=None, until_timestamp=None, limit=None, order_by_timestamp=True, order_ascending=True):
    def get_insulin_administrations(self, user_pk=None, from_timestamp=None, until_timestamp=None, limit=None, order_by_timestamp=True, order_ascending=True):
    def get_traits(self, user_pk, kind, from_timestamp=None, until_timestamp=None, limit=None, order_by_timestamp=True, order_ascending=True):
    def get_configuration(self, user_pk, key):

    def add_descriptive_observer(self, obs):
    """
    def __init__(self, descriptive_repository_class=None):
        assert descriptive_repository_class
        super(DiaCore, self).__init__(descriptive_repository_class())

        " list of predictive systems to use "
        self._predictive_systems = []

    @property    
    def all_predictive_systems(self):
        return self._predictive_systems
    
    def add_predictive_system(self, system):
        assert isinstance(system, AbstractPredictiveSystem),\
            "Invalid AbstractPredictiveSystem provided"

        assert system.unique_identificator not in \
            [s.unique_identificator for s in self._predictive_systems],\
            "unique_identificator of system provided is not unique"

        if system in self._predictive_systems:
            return

        " add the system "
        self._predictive_systems.append(system)



    " It will be request a recommendation only to one predictive system "
    def get_recommendation(self, context, predictive_system_unique_identificator=None):
        assert len(self._predictive_systems) > 0, "There is no predictive systems added"
        assert isinstance(context, PredictiveRequestContext)
        
        unique_id = predictive_system_unique_identificator
        assert unique_id in [system.unique_identificator for system in self._predictive_systems],\
            "There is no predictive system with unique id {}".format(unique_id)

        for system in self._predictive_systems:
            if system.unique_identificator == unique_id:
                recommendation = system.get_recommendation(context)
                assert isinstance(recommendation, RecommendationResponse)
                return recommendation
        """
        For the response returned see dia.interfaces.Recommendation
        """


"""
Here we wire all the elements in which diacore depends on
resulting in a full working solution.
"""
diacore = DiaCore(settings.DESCRIPTIVE_REPOSITORY)

for System in settings.PREDICTIVE_SYSTEMS:
    diacore.add_predictive_system(System())


"""
This main object is the object to help to work on dia.

One instance per user

user must be an instance of dia.models.User
timestamp must be a flat integer
"""
class DiaUserHandler(object):
    def __init__(self, user_pk=None, timestamp=None):
        self.diacore = diacore
        self.user = self.diacore.get_user(user_pk)
        self.timestamp = timestamp
        self.timezone = self.diacore.get_configuration(self.user.pk, ConfigurationKey.TIMEZONE).value

    def _asign_ts_obj(self, timestamp):
        assert timestamp or self.timestamp
        """
        We work with dia.time.Timestamp objects internally.
        This object has all the timezone information and conversion methods
        to help working between timestamps and aware datetimes.
        """
        if timestamp:
            ts = timestamp
        if self.timestamp:
            ts = self.timestamp
        timestamp_obj = Timestamp(ts)
        timestamp_obj.change_tz(self.timezone)
        return timestamp_obj
        
        
    def add_glucose(self, timestamp=None, mgdl_level=None):
        glucose = GlucoseLevel(
            user_pk=self.user.pk,
            timestamp=self._asign_ts(timestamp).ts,
            mgdl_level=mgdl_level
        )
        self.diacore.add_glucose_level(glucose)

    def add_activity(self, timestamp=None, intensity=None, minutes=None):
        activity = Activity(
            user_pk=self.user.pk,
            timestamp=self._asign_ts(timestamp).ts,
            intensity=intensity,
            minutes=minutes
        )
        self.diacore.add_activity(activity)
        
    def add_feeding(self, timestamp=None, total_gr=0, total_ml=0, carb_gr=0, protein_gr=0, fat_gr=0, fiber_gr=0, alcohol_gr=0):
        feeding = Feeding(
            user_pk=self.user.pk,
            timestamp=self._asign_ts(timestamp).ts,
            total_gr=total_gr,
            total_ml=total_ml,
            carb_gr=carb_gr,
            protein_gr=protein_gr,
            fat_gr=fat_gr,
            fiber_gr=fiber_gr,
            alcohol_gr=alcohol_gr
        )
        self.diacore.add_feeding(feeding)

    def add_insulin_administration(self, timestamp=None, insulin_type=None, insulin_units=None):
        insulin = InsulinAdministration(
            user_pk=self.user.pk,
            timestamp=self._asign_ts(timestamp).ts,
            insulin_type=insulin_type,
            insulin_units=insulin_units
        )
        self.diacore.add_insulin_administration(insulin)
    
    def update_trait(self, timestamp=None, kind=None, value=None):
        trait = Trait(
            user_pk=self.user.pk,
            timestamp=self._asign_ts(timestamp).ts,
            kind=kind,
            value=value
        )
        self.diacore.update_trait(trait)
    
    def update_configuration(self, key=None, value=None):
        config = Configuration(
            user_pk=self.user.pk, key=key, value=value
        )
        self.diacore.update_configuration(config)
