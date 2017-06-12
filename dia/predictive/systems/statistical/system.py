from dia.predictive.interfaces import AbstractPredictiveSystem
from dia.interfaces import AbstractDescriptiveRepositoryObserver

from .analysis.basics import hba1c
from .analysis.basics import basalinsulin
from .analysis.groupings import grouped_feedings


class StatisticalPredictiveSystem(AbstractDescriptiveRepositoryObserver, AbstractPredictiveSystem):
    
    def __init__(self, descriptive_repository):
        self._descriptive_repository = descriptive_repository
    
    @property
    def descriptive_repository(self):
        return self._descriptive_repository

    """
    To recalculate if necessary
    """
    def on_glucose_added(self, glucose):
        hba1c.recalculate_hba1c(glucose)
        grouped_feedings.glucose_inserted(glucose)

    def on_activity_added(self, activity):
        pass

    def on_insulin_administration_added(self, insulin_administration):
        basalinsulin.basal_checks(insulin_administration)

    def on_feeding_added(self, feeding):
        pass

    def on_trait_change(self, trait):
        pass

    """
    For the recommendation
    """
    def get_recommendation(self, user_pk, utc_timestamp):
        pass

    """
    This is the unique identificator. Must be unique between all systems
    """
    @property
    def unique_identificator(self):
        return "predictive.systems.statisticalpredictivesystem"



