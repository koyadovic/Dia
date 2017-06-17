from predictive.interfaces import AbstractPredictiveSystem
from dia.interfaces import AbstractDescriptiveRepositoryObserver



class StatisticalV2PredictiveSystem(AbstractDescriptiveRepositoryObserver, AbstractPredictiveSystem):
    
    def __init__(self, descriptive_repository):
        self._descriptive_repository = descriptive_repository
    
    @property
    def descriptive_repository(self):
        return self._descriptive_repository

    """
    To recalculate if necessary
    """
    def on_glucose_added(self, glucose):
        pass

    def on_activity_added(self, activity):
        pass

    def on_insulin_administration_added(self, insulin_administration):
        pass

    def on_feeding_added(self, feeding):
        pass

    def on_trait_change(self, trait):
        pass

    """
    For the recommendation
    """
    def get_recommendation(self, context):
        pass

    """
    This is the unique identificator. Must be unique between all systems
    """
    @property
    def unique_identificator(self):
        return "predictive.systems.statisticalv2predictivesystem"
    
    @property
    def name(self):
        return "Statistical v2 Predictive System v0.1"
