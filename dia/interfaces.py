# -*- coding: utf-8 -*-

from abc import ABCMeta, abstractmethod

from dia.models import GlucoseLevel, Activity, Trait, InsulinAdministration, Feeding


class AbstractDescriptiveRepository:
    __metaclass__ = ABCMeta

    """
    pk references to something that could be used to identify to each element
    user_pk exactly equal. It will have to identify only one user inside the system
    """

    @abstractmethod
    def add_glucose_level(self, user_pk, utc_timestamp, mgdl_level):
        "Must return the GlucoseLevel instance added"
        raise NotImplementedError

    @abstractmethod
    def get_glucoses(self, user_pk, from_utc_timestamp=None,
        until_utc_timestamp=None, mgdl_level_above=None, mgdl_level_below=None,
        limit=None, order_by_utc_timestamp=True, order_ascending=True):
        "Must be returned a List of GlucoseLevel instances. [] if empty"
        raise NotImplementedError

    @abstractmethod
    def add_activity(self, user_pk, utc_timestamp, intensity, minutes):
        "Must return the Activity instance added"
        raise NotImplementedError

    @abstractmethod
    def get_activities(self, user_pk, from_utc_timestamp=None,
        until_utc_timestamp=None, limit=None, order_by_utc_timestamp=True,
        order_ascending=True):
        "Must be returned a List of Activity instances. [] if empty"
        raise NotImplementedError

    @abstractmethod
    def add_insulin_administration(self, user_pk, utc_timestamp, insulin_type,
        insulin_units):
        "Must return the InsulinAdministration instance added"
        raise NotImplementedError

    @abstractmethod
    def get_insulin_administrations(self, user_pk, from_utc_timestamp=None,
        until_utc_timestamp=None, insulin_types_in=None, limit=None,
        order_by_utc_timestamp=True, order_ascending=True):
        "Must be returned a List of InsulinAdministration instances. [] if empty"
        raise NotImplementedError


    @abstractmethod
    def add_feeding(self, user_pk, utc_timestamp, total_gr=0, total_ml=0,
        carb_gr=0, protein_gr=0, fat_gr=0, fiber_gr=0, alcohol_gr=0):
        "Must return the Feeding instance added"
        raise NotImplementedError

    @abstractmethod
    def get_feedings(self, user_pk, from_utc_timestamp=None,
        until_utc_timestamp=None, limit=None, order_by_utc_timestamp=True,
        order_ascending=True):
        "Must be returned a List of Feeding instances. [] if empty"
        raise NotImplementedError



    @abstractmethod
    def update_trait(self, user_pk, utc_timestamp, kind, value):
        """
        kind is one of dia.models.TraitKind
        value's are also specified on the same model class
        must be returned the Trait object added
        """
        raise NotImplementedError
    
    """
    get_traits("1", whatever, order_ascending=False, limit=1) nos daria el ultimo
    """
    @abstractmethod
    def get_traits(self, user_pk, trait, from_utc_timestamp=None,
        until_utc_timestamp=None, limit=None, order_by_utc_timestamp=True,
        order_ascending=True):
        "Must be returned a List of Trait instances. [] if empty"
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
                utc_timestamp=glucose.utc_timestamp,
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
                utc_timestamp=activity.utc_timestamp,
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
                utc_timestamp=feeding.utc_timestamp,
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
                utc_timestamp=insulin.utc_timestamp,
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
                utc_timestamp=trait.utc_timestamp,
                trait=trait.trait,
                value=trait.value
            )
        
        if trait.pk:
            self._notify_descriptive_observers(trait)

        return trait


    """
    All the 'query' like methods
    """
    def get_glucoses(self, user_pk, from_utc_timestamp=None,
        until_utc_timestamp=None, mgdl_level_above=None, mgdl_level_below=None,
        limit=None, order_by_utc_timestamp=True, order_ascending=True):

        return self._r.get_glucoses(
            user_pk=user_pk,
            from_utc_timestamp=from_utc_timestamp,
            until_utc_timestamp=until_utc_timestamp,
            mgdl_level_above=mgdl_level_above,
            mgdl_level_below=mgdl_level_below,
            limit=limit
        )


    def get_activities(self, user_pk, from_utc_timestamp=None,
        until_utc_timestamp=None, limit=None, order_by_utc_timestamp=True,
        order_ascending=True):

        return self._r.get_activities(
            user_pk=user_pk,
            from_utc_timestamp=from_utc_timestamp,
            until_utc_timestamp=until_utc_timestamp,
            limit=limit
        )


    def get_traits(self, user_pk, trait, from_utc_timestamp=None,
        until_utc_timestamp=None, limit=None, order_by_utc_timestamp=True,
        order_ascending=True):

        return self._r.get_traits(
            user_pk=user_pk,
            trait=trait,
            from_utc_timestamp=from_utc_timestamp,
            until_utc_timestamp=until_utc_timestamp,
            limit=limit,
            order_by_utc_timestamp=order_by_utc_timestamp,
            order_ascending=order_ascending
        )
        

    def get_feedings(self, user_pk, from_utc_timestamp=None,
        until_utc_timestamp=None, limit=None, order_by_utc_timestamp=True,
        order_ascending=True):

        return self._r.get_feedings(
            user_pk=user_pk,
            from_utc_timestamp=from_utc_timestamp,
            until_utc_timestamp=until_utc_timestamp,
            limit=limit
        )


    def get_insulin_administrations(self, user_pk, from_utc_timestamp=None,
        until_utc_timestamp=None, limit=None, order_by_utc_timestamp=True,
        order_ascending=True):

        return self._r.get_insulin_administrations(
            user_pk=user_pk,
            from_utc_timestamp=from_utc_timestamp,
            until_utc_timestamp=until_utc_timestamp,
            limit=limit
        )


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


