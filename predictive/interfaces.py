# -*- coding: utf-8 -*-

from abc import ABCMeta, abstractmethod, abstractproperty


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
    def get_recommendation(self):
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

