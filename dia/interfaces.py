# -*- coding: utf-8 -*-

from abc import ABCMeta, abstractmethod, abstractproperty

from dia.models import GlucoseLevel, Activity, Trait, InsulinAdministration, Feeding,\
    Configuration


class AbstractDescriptiveRepository:
    __metaclass__ = ABCMeta

    """
    pk references to something that could be used to identify to each element
    user_pk exactly equal. It will have to identify only one user inside the system
    timestamp is an integer, not dia.time.Timestamp object
    """

    @abstractmethod
    def add_glucose_level(self, user_pk, timestamp, mgdl_level):
        "Must return the GlucoseLevel instance added"
        raise NotImplementedError

    @abstractmethod
    def add_activity(self, user_pk, timestamp, intensity, minutes):
        "Must return the Activity instance added"
        raise NotImplementedError

    @abstractmethod
    def add_insulin_administration(self, user_pk, timestamp, insulin_type, insulin_units):
        "Must return the InsulinAdministration instance added"
        raise NotImplementedError

    @abstractmethod
    def add_feeding(self, user_pk, timestamp, total_gr=0, total_ml=0,
        carb_gr=0, protein_gr=0, fat_gr=0, fiber_gr=0, alcohol_gr=0):
        "Must return the Feeding instance added"
        raise NotImplementedError

    @abstractmethod
    def update_trait(self, user_pk, timestamp, kind, value):
        """
        kind is one of dia.models.TraitKind
        value's are also specified on the same model class
        must be returned the Trait object added
        """
        raise NotImplementedError

    @abstractmethod
    def update_configuration(self, user_pk, key, value):
        """
        key is one of dia.models.ConfigurationKey
        It's only needed to store one value per key, not new records per each change
        value is algo specified in the same model class
        """
        raise NotImplementedError

    """
    Querys
    """    
    @abstractmethod
    def get_glucoses(self, user_pk, from_timestamp=None,
        until_timestamp=None, mgdl_level_above=None, mgdl_level_below=None,
        limit=None, order_by_timestamp=True, order_ascending=True):
        "Must be returned a List of GlucoseLevel instances. [] if empty"
        raise NotImplementedError

    @abstractmethod
    def get_activities(self, user_pk, from_timestamp=None,
        until_timestamp=None, limit=None, order_by_timestamp=True,
        order_ascending=True):
        "Must be returned a List of Activity instances. [] if empty"
        raise NotImplementedError

    @abstractmethod
    def get_insulin_administrations(self, user_pk, from_timestamp=None,
        until_timestamp=None, insulin_types_in=None, limit=None,
        order_by_timestamp=True, order_ascending=True):
        "Must be returned a List of InsulinAdministration instances. [] if empty"
        raise NotImplementedError

    @abstractmethod
    def get_feedings(self, user_pk, from_timestamp=None,
        until_timestamp=None, limit=None, order_by_timestamp=True,
        order_ascending=True):
        "Must be returned a List of Feeding instances. [] if empty"
        raise NotImplementedError
  
    """
    get_traits("1", whatever, order_ascending=False, limit=1) nos daria el ultimo
    """
    @abstractmethod
    def get_traits(self, user_pk, kind, from_timestamp=None,
        until_timestamp=None, limit=None, order_by_timestamp=True,
        order_ascending=True):
        "Must be returned a List of Trait instances. [] if empty"
        raise NotImplementedError

    @abstractmethod
    def get_configuration(self, user_pk, key):
        "Must be returned the value of the key requested"
        raise NotImplementedError

    @abstractmethod
    def get_user(self, user_pk):
        "Must be returned the value of the key requested"
        raise NotImplementedError


"""
All the DescriptiveRepositoryObserver observers must implement this interface
and use the methods add_descriptive_observer of the adapter to declare itself as
descriptive_observer for the events
"""
class AbstractDescriptiveRepositoryObserver:
    __metaclass_ = ABCMeta

    @abstractmethod
    def on_glucose_added(self, glucose):
        raise NotImplementedError

    @abstractmethod
    def on_activity_added(self, activity):
        raise NotImplementedError

    @abstractmethod
    def on_insulin_administration_added(self, insulin_administration):
        raise NotImplementedError

    @abstractmethod
    def on_feeding_added(self, feeding):
        raise NotImplementedError

    @abstractmethod
    def on_trait_change(self, trait):
        raise NotImplementedError


class DescriptiveRepositoryAdapter(object):
    _r = None
    
    def __init__(self, concrete_repository):
        assert isinstance(concrete_repository, AbstractDescriptiveRepository),\
            "Invalid AbstractDescriptiveRepository implementation specified"
        self._r = concrete_repository

    """
    A esta clase es a la que el modulo dia tendra que llamar para comunicarse
    indirectamente con la implementacion concreta.

    Tendra que traducir las respuestas que esperamos en la interfaz con
    datatypes o estructuras basicas a modelos descritos internamente.
    """

    """
    All the 'add' kind methods.
    """
    def add_glucose_level(self, glucose):
        assert isinstance(glucose, GlucoseLevel),\
            "Invalid instance of GlucoseLevel provided"
        
        glucose = self._r.add_glucose_level(
                user_pk=glucose.user_pk,
                timestamp=glucose.timestamp,
                mgdl_level=glucose.mgdl_level
            )

        if glucose.pk:
            self._notify_descriptive_observers(glucose)
        
        return glucose

    def add_activity(self, activity):
        assert isinstance(activity, Activity),\
            "Invalid instance of Activity provided"
        activity = self._r.add_activity(
                user_pk=activity.user_pk,
                timestamp=activity.timestamp,
                intensity=activity.intensity,
                minutes=activity.minutes
            )
        
        if activity.pk:
            self._notify_descriptive_observers(activity)
        
        return activity

    def add_feeding(self, feeding):
        assert isinstance(feeding, Feeding),\
            "Invalid instance of Feeding provided"

        feeding = self._r.add_feeding(
                user_pk=feeding.user_pk,
                timestamp=feeding.timestamp,
                total_gr=feeding.total_gr,
                total_ml=feeding.total_ml,
                carb_gr=feeding.carb_gr,
                protein_gr=feeding.protein_gr,
                fat_gr=feeding.fat_gr,
                fiber_gr=feeding.fiber_gr,
                alcohol_gr=feeding.alcohol_gr
            )
        if feeding.pk:
            self._notify_descriptive_observers(feeding)

        return feeding

    def add_insulin_administration(self, insulin):
        assert isinstance(insulin, InsulinAdministration),\
            "Invalid instance of InsulinAdministration provided"

        insulin = self._r.add_insulin_administration(
                user_pk=insulin.user_pk,
                timestamp=insulin.timestamp,
                insulin_type=insulin.insulin_type,
                insulin_units=insulin.insulin_units
            )
        
        if insulin.pk:
            self._notify_descriptive_observers(insulin)

        return insulin

    def update_trait(self, trait):
        assert isinstance(trait, Trait),\
            "Invalid instance of Trait provided"
            
        trait = self._r.update_trait(
                user_pk=trait.user_pk,
                timestamp=trait.timestamp,
                kind=trait.kind,
                value=trait.value
            )
        
        if trait.pk:
            self._notify_descriptive_observers(trait)

        return trait

    def update_configuration(self, config):
        assert isinstance(config, Configuration),\
            "Invalid instance of Configuration provided"
            
        config = self._r.update_configuration(user_pk=config.user_pk, key=config.key, value=config.value)
        
        return config


    """
    All the 'query' like methods
    """
    def get_glucoses(self, user_pk, from_timestamp=None,
        until_timestamp=None, mgdl_level_above=None, mgdl_level_below=None,
        limit=None, order_by_timestamp=True, order_ascending=False):

        return self._r.get_glucoses(
            user_pk,
            from_timestamp=from_timestamp,
            until_timestamp=until_timestamp,
            mgdl_level_above=mgdl_level_above,
            mgdl_level_below=mgdl_level_below,
            limit=limit,
            order_by_timestamp=order_by_timestamp,
            order_ascending=order_ascending
        )


    def get_activities(self, user_pk, from_timestamp=None,
        until_timestamp=None, limit=None, order_by_timestamp=True,
        order_ascending=False):

        return self._r.get_activities(
            user_pk,
            from_timestamp=from_timestamp,
            until_timestamp=until_timestamp,
            limit=limit,
            order_by_timestamp=order_by_timestamp,
            order_ascending=order_ascending
        )


    def get_traits(self, user_pk, kind, from_timestamp=None,
        until_timestamp=None, limit=None, order_by_timestamp=True,
        order_ascending=False):

        return self._r.get_traits(
            user_pk,
            kind=kind,
            from_timestamp=from_timestamp,
            until_timestamp=until_timestamp,
            limit=limit,
            order_by_timestamp=order_by_timestamp,
            order_ascending=order_ascending
        )

    def get_configuration(self, user_pk, key):
        """
        This must return a dia.model.Configuration class.
        If the key don't exist, must create one using as value the
        default value for the key requested from dia.models.ConfigurationKey.DefaultValues dict.
        """
        return self._r.get_configuration(user_pk, key=key)
        

    def get_feedings(self, user_pk, from_timestamp=None,
        until_timestamp=None, limit=None, order_by_timestamp=True,
        order_ascending=False):

        return self._r.get_feedings(
            user_pk,
            from_timestamp=from_timestamp,
            until_timestamp=until_timestamp,
            limit=limit,
            order_by_timestamp=order_by_timestamp,
            order_ascending=order_ascending
        )


    def get_insulin_administrations(self, user_pk, from_timestamp=None,
        until_timestamp=None, limit=None, order_by_timestamp=True,
        order_ascending=False, insulin_types_in=[]):

        return self._r.get_insulin_administrations(
            user_pk,
            from_timestamp=from_timestamp,
            until_timestamp=until_timestamp,
            limit=limit,
            order_by_timestamp=order_by_timestamp,
            order_ascending=order_ascending,
            insulin_types_in=insulin_types_in
        )
    
    def get_user(self, user_pk):
        return self._r.get_user(user_pk=user_pk)


    """
    Observers
    """
    _descriptive_observers = []
    def add_descriptive_repository_observer(self, obs):
        assert isinstance(obs, AbstractDescriptiveRepositoryObserver),\
            "Invalid implementation of AbstractDescriptiveRepositoryObserver provided."
        self._descriptive_observers.append(obs)

    def _notify_descriptive_observers(self, target):
        for o in self._descriptive_observers:
            if isinstance(target, GlucoseLevel):
                o.on_glucose_added(target)

            elif isinstance(target, Activity):
                o.on_activity_added(target)

            elif isinstance(target, Feeding):
                o.on_feeding_added(target)

            elif isinstance(target, InsulinAdministration):
                o.on_insulin_administration_added(target)

            elif isinstance(target, Trait):
                o.on_trait_change_added(target)




"""
All predictive modules must implement this interface.
"""
class AbstractPredictiveSystem:
    __metaclass__ = ABCMeta
    """
    With this method, there is only two possibilities that can occurs:
    1.- If there is an insulin administration event added:
    it must be returned a Feeding event, 
    
    2.- If there is a Feeding event added:
    it must be returned a InsulinAdministration event or a modification
    in de Feeding event and a InsulinAdministration event, the two.
    """
    @abstractmethod
    def get_recommendation(self, context):
        raise NotImplementedError

    """
    This property must be unique between differents predictive implementations
    """
    @abstractproperty
    def unique_identificator(self):
        raise NotImplementedError
    
    """
    This property must show the name of the system in a human readable way.
    """
    @abstractproperty
    def name(self):
        raise NotImplementedError

    def __str__(self):
        return self.name



from datetime import datetime
import pytz

class PredictiveRequestContext(object):
    """
    This is the main object that can be used to situate every query
    in a date and time point for a single user.
    
    Is used to detail the context in which a recommendation request is made.
    """
    def __init__(self, user_pk, timestamp, tzinfo=pytz.utc):
        self._u = user_pk
        self._ts = timestamp
        self._tz = tzinfo

    @property
    def user_pk(self):
        return self._u
    
    @property
    def timestamp(self):
        return self._ts
    
    @property
    def tzinfo(self):
        return self._tz
    
    @property
    def utc_datetime(self):
        return datetime.fromtimestamp(self._ts, pytz.utc)
    
    @property
    def local_datetime(self):
        return self.utc_datetime.astimezone(self._tz)
    
    def __iter__(self):
        " With this, only with a dict(obj) the object is automatically converted as a dict. "
        yield 'user_pk', self.user_pk
        yield 'timestamp', self.timestamp
        yield 'tzinfo', str(self.tzinfo)
    
    def __str__(self):
        return '{}: {}'.format(type(self).__name__, dict(self))


"""
This is for the recommendations responses

Predictive systems must return instances of this object.

The recommendation is compound of InsulinAdministration, Feeding
or Activity events that must be followed to maintain glucose levels
in range. Some can be new events, and others can be changed events
"""

class RecommendationResponse(object):
    def __init__(self, predictive_unique_id):
        self._new_events = []
        self._changed_events = []
        self._unique_id = predictive_unique_id
    
    def _check_event(self, event):
        assert isinstance(event, InsulinAdministration) or \
            isinstance(event, Activity) or isinstance(event, Feeding)

    def append_new_event(self, event):
        self._check_event(event)
        self._new_events.append(event)
    
    @property
    def new_events(self):
        return self._new_events

    def append_changed_event(self, event):
        self._check_event(event)
        self._changed_events.append(event)
    
    @property
    def changed_events(self):
        return self._changed_events
    
    @property
    def predictive_unique_id(self):
        """
        This is the unique indentificator of the predictive system that created
        the recommendation.
        """
        return self._unique_id



