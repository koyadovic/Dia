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
        # debe retornar la glucosa aniadida. Si todo fue bien pk tendra algun valor
        raise NotImplementedError

    @abstractmethod
    def get_glucoses(self, user_pk, from_utc_timestamp=None,
        until_utc_timestamp=None, mgdl_level_above=None, mgdl_level_below=None,
        limit=None, order_by_utc_timestamp=True, order_ascending=True):
        """
        user_pk(string or int): el pk que identifica al usuario para el que se realiza la query
        from_utc_timestamp(long): el utc_timestamp desde el que se recogeran datos.
        until_utc_timestamp(long): el utc_timestamp hasta el que se recogeran datos.
        mgdl_level_above(int): se tendran que devolver niveles mayores que el especificado
        mgdl_level_below(int): se tendran que devolver niveles menores que el esperificado
        limit(int): limita el numero de resultados

        se esperara como respuesta un List de Dictionaries, por ejemplo:
        {
            pk: 1,
            user_pk: 1,
            utc_timestamp: 11847378432,
            mgdl_level: 120
        },
        {
            pk: 2,
            user_pk: 1,
            utc_timestamp: 11847654465,
            mgdl_level: 133
        },
        ... etc
        """
        raise NotImplementedError

    @abstractmethod
    def add_activity(self, user_pk, utc_timestamp, intensity, minutes):
        # debe retornar la actividad aniadida. Si todo fue ok, pk tendra algun valor
        raise NotImplementedError

    @abstractmethod
    def get_activities(self, user_pk, from_utc_timestamp=None,
        until_utc_timestamp=None, limit=None, order_by_utc_timestamp=True,
        order_ascending=True):
        """
        user_pk(string): el pk que identifica al usuario para el que se realiza la query
                tendra que ser convertido al datatype usado fuera del sistema.
        from_utc_timestamp(long): el utc_timestamp desde el que se recogeran datos.
        until_utc_timestamp(long): el utc_timestamp hasta el que se recogeran datos.
        limit(int): limita el numero de resultados

        se esperara como respuesta un List de Dictionaries, por ejemplo:
        {
            pk: 1,
            user_pk: 1,
            utc_timestamp: 11847378432,
            intensity: 2,
            minutes: 40
        },
        {
            pk: 2,
            user_pk: 1,
            utc_timestamp: 11847654465,
            intensity: 2,
            minutes: 40
        },
        ... etc
        """
        raise NotImplementedError


    @abstractmethod
    def add_insulin_administration(self, user_pk, utc_timestamp, insulin_type,
        insulin_units):
        # debe retornar la insulina aniadida. si todo ok, pk deberia tener algun valor
        raise NotImplementedError

    @abstractmethod
    def get_insulin_administrations(self, user_pk, from_utc_timestamp=None,
        until_utc_timestamp=None, insulin_types_in=None, limit=None,
        order_by_utc_timestamp=True, order_ascending=True):
        """
        user_pk(string): el pk que identifica al usuario para el que se realiza la query
                tendra que ser convertido al datatype usado fuera del sistema.
        from_utc_timestamp(long): el utc_timestamp desde el que se recogeran datos.
        until_utc_timestamp(long): el utc_timestamp hasta el que se recogeran datos.
        insulin_types_in(list): se tendran que devolver tipos entre los especifiados
        limit(int): limita el numero de resultados

        se esperara como respuesta un List de Dictionaries, por ejemplo:
        {
            pk: 1,
            user_pk: 1,
            utc_timestamp: 11847378432,
            insulin_type: 1,
            insulin_units: 3
        },
        {
            pk: 2,
            user_pk: 1,
            utc_timestamp: 11847654465,
            insulin_type: 1,
            insulin_units: 3
        },
        ... etc
        """
        raise NotImplementedError


    @abstractmethod
    def add_feeding(self, user_pk, utc_timestamp, total_gr=0, total_ml=0,
        carb_gr=0, protein_gr=0, fat_gr=0, fiber_gr=0, alcohol_gr=0):
        # debe retornar el feeding aniadido. Si todo ok, pk deberia tener algun valor
        raise NotImplementedError

    @abstractmethod
    def get_feedings(self, user_pk, from_utc_timestamp=None,
        until_utc_timestamp=None, limit=None, order_by_utc_timestamp=True,
        order_ascending=True):

        """
        user_pk(string): el pk que identifica al usuario para el que se realiza la query
                tendra que ser convertido al datatype usado fuera del sistema.
        from_utc_timestamp(long): el utc_timestamp desde el que se recogeran datos.
        until_utc_timestamp(long): el utc_timestamp hasta el que se recogeran datos.
        limit(int): limita el numero de resultados

        se esperara como respuesta un List de Dictionaries, por ejemplo:
        {
            pk: 1,
            user_pk: 1,
            utc_timestamp: 11847378432,
            total_gr: 60,
            total_ml: 0,
            carb_gr: 30,
            protein_gr: 2,
            fat_gr: 5,
            fiber_gr: 2,
            alcohol_gr: 0
        },
        {
            pk: 2,
            user_pk: 1,
            utc_timestamp: 11847654465,
            total_gr: 60,
            total_ml: 0,
            carb_gr: 30,
            protein_gr: 2,
            fat_gr: 5,
            fiber_gr: 2,
            alcohol_gr: 0
        },
        ... etc
        """
        raise NotImplementedError



    @abstractmethod
    def update_trait(self, user_pk, utc_timestamp, trait, value):
        """
        trait is one of dia.models.descriptions.Trait.ALL_TRAITS
        the value datatypes are also specified on the same model class
        must be returned the Trait object added, if all ok, pk must have any value
        """
        raise NotImplementedError
    
    """
    get_traits("1", whatever, order_ascending=False, limit=1) nos daria el ultimo
    """
    @abstractmethod
    def get_traits(self, user_pk, trait, from_utc_timestamp=None,
        until_utc_timestamp=None, limit=None, order_by_utc_timestamp=True,
        order_ascending=True):
        """
        Must return the last and most up to date trait specified.
        must return a dictionary in the following form:
        Please, see dia.models.descriptions.Trait class
        {
            pk: 1,
            user_pk: 1,
            utc_timestamp: 11847378432,
            trait: 4,
            value: 23
        },
        {
            pk: 2,
            user_pk: 1,
            utc_timestamp: 14347378432,
            trait: 4,
            value: 27
        }, ... etc

        value must conform the datatype of the trait selected.
        """
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
    
    def __init__(self, repository):
        assert isinstance(repository, AbstractDescriptiveRepository),\
            "Invalid AbstractDescriptiveRepository implementation specified"
        self._r = repository

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
        if self._r.add_glucose_level(
                user_pk=glucose.user_pk,
                utc_timestamp=glucose.utc_timestamp,
                mgdl_level=glucose.mgdl_level
            ):
            self._notify_descriptive_observers(glucose)
            return True
        return False

    def add_activity(self, activity):
        assert isinstance(activity, Activity),\
            "Invalid instance of Activity provided"
        if self._r.add_activity(
                user_pk=activity.user_pk,
                utc_timestamp=activity.utc_timestamp,
                intensity=activity.intensity,
                minutes=activity.minutes
            ):
            self._notify_descriptive_observers(activity)
            return True
        return False

    def add_feeding(self, feeding):
        assert isinstance(feeding, Feeding),\
            "Invalid instance of Feeding provided"
        if self._r.add_feeding(
                user_pk=feeding.user_pk,
                utc_timestamp=feeding.utc_timestamp,
                total_gr=feeding.total_gr,
                total_ml=feeding.total_ml,
                carb_gr=feeding.carb_gr,
                protein_gr=feeding.protein_gr,
                fat_gr=feeding.fat_gr,
                fiber_gr=feeding.fiber_gr,
                alcohol_gr=feeding.alcohol_gr
            ):
            self._notify_descriptive_observers(feeding)
            return True
        return False

    def add_insulin_administration(self, insulin):
        assert isinstance(insulin, InsulinAdministration),\
            "Invalid instance of InsulinAdministration provided"
        if self._r.add_insulin_administration(
                user_pk=insulin.user_pk,
                utc_timestamp=insulin.utc_timestamp,
                insulin_type=insulin.insulin_type,
                insulin_units=insulin.insulin_units
            ):
            self._notify_descriptive_observers(insulin)
            return True
        return False

    def update_trait(self, trait):
        assert isinstance(trait, Trait),\
            "Invalid instance of Trait provided"
        if self._r.update_trait(
                user_pk=trait.user_pk,
                utc_timestamp=trait.utc_timestamp,
                trait=trait.trait,
                value=trait.value
            ):
            self._notify_descriptive_observers(trait)
            return True
        return False


    """
    All the 'query' like methods
    """
    def get_glucoses(self, user_pk, from_utc_timestamp=None,
        until_utc_timestamp=None, mgdl_level_above=None, mgdl_level_below=None,
        limit=None, order_by_utc_timestamp=True, order_ascending=True):

        raw_glucose_list = self._r.get_glucoses(
            user_pk=user_pk,
            from_utc_timestamp=from_utc_timestamp,
            until_utc_timestamp=until_utc_timestamp,
            mgdl_level_above=mgdl_level_above,
            mgdl_level_below=mgdl_level_below,
            limit=limit
        )

        glucose_list = [
            GlucoseLevel(
                    pk=raw_glucose['pk'],
                    user_pk=raw_glucose['user_pk'],
                    utc_timestamp=raw_glucose['utc_timestamp'],
                    mgdl_level=raw_glucose['mgdl_level']
                ) for raw_glucose in raw_glucose_list
            ]

        return glucose_list

    def get_activities(self, user_pk, from_utc_timestamp=None,
        until_utc_timestamp=None, limit=None, order_by_utc_timestamp=True,
        order_ascending=True):

        raw_activities = self._r.get_activities(
            user_pk=user_pk,
            from_utc_timestamp=from_utc_timestamp,
            until_utc_timestamp=until_utc_timestamp,
            limit=limit
        )
        
        activities = [
            Activity(
                pk=activity['pk'],
                user_pk=activity['user_pk'],
                utc_timestamp=activity['utc_timestamp'],
                intensity=activity['intensity'],
                minutes=activity['minutes']
            ) for activity in raw_activities
        ]

        return activities


    def get_traits(self, user_pk, trait, from_utc_timestamp=None,
        until_utc_timestamp=None, limit=None, order_by_utc_timestamp=True,
        order_ascending=True):

        raw_traits = self._r.get_traits(
            user_pk=user_pk,
            trait=trait,
            from_utc_timestamp=from_utc_timestamp,
            until_utc_timestamp=until_utc_timestamp,
            limit=limit,
            order_by_utc_timestamp=order_by_utc_timestamp,
            order_ascending=order_ascending
        )
        
        traits = [
            Trait(
                pk=raw_trait['pk'],
                user_pk=raw_trait['user_pk'],
                utc_timestamp=raw_trait['utc_timestamp'],
                trait=raw_trait['trait'],
                value=raw_trait['value'],
            ) for raw_trait in raw_traits
        ]
        
        return traits

    def get_feedings(self, user_pk, from_utc_timestamp=None,
        until_utc_timestamp=None, limit=None, order_by_utc_timestamp=True,
        order_ascending=True):

        raw_feedings = self._r.get_feedings(
            user_pk=user_pk,
            from_utc_timestamp=from_utc_timestamp,
            until_utc_timestamp=until_utc_timestamp,
            limit=limit
        )
        feedings = [
            Feeding(
                pk=feeding['pk'],
                user_pk=feeding['user_pk'],
                utc_timestamp=feeding['utc_timestamp'],
                total_gr=feeding['total_gr'],
                total_ml=feeding['total_ml'],
                carb_gr=feeding['carb_gr'],
                protein_gr=feeding['protein_gr'],
                fat_gr=feeding['fat_gr'],
                fiber_gr=feeding['fiber_gr'],
                alcohol_gr=feeding['alcohol_gr'],
            ) for feeding in raw_feedings
        ]

        return feedings

    def get_insulin_administrations(self, user_pk, from_utc_timestamp=None,
        until_utc_timestamp=None, limit=None, order_by_utc_timestamp=True,
        order_ascending=True):

        raw_insulins = self._r.get_insulin_administrations(
            user_pk=user_pk,
            from_utc_timestamp=from_utc_timestamp,
            until_utc_timestamp=until_utc_timestamp,
            limit=limit
        )

        insulins = [
            InsulinAdministration(
                pk=insulin['pk'],
                user_pk=insulin['user_pk'],
                utc_timestamp=insulin['utc_timestamp'],
                insulin_type=insulin['insulin_type'],
                insulin_units=insulin['insulin_units']
            ) for insulin in raw_insulins
        ]

        return insulins


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


