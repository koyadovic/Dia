from dia.interfaces import AbstractDescriptiveRepositoryObserver,\
    AbstractPredictiveSystem

from .analysis.basics import hba1c
from .analysis.basics import basalinsulin
from .analysis.groupings import grouped_feedings

from dia.core import diacore

class StatisticalPredictiveSystem(AbstractDescriptiveRepositoryObserver, AbstractPredictiveSystem):
    
    def __init__(self):
        diacore.add_descriptive_repository_observer(self)
        
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

    def on_trait_change_added(self, trait):
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
        return "predictive.systems.statisticalpredictivesystem"
    
    @property
    def name(self):
        return "Statistical Predictive System v0.1"



