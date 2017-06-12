from dia.predictive.interfaces import AbstractPredictiveSystem
from dia.interfaces import AbstractDescriptiveRepositoryObserver


class StatisticalPredictiveSystem(AbstractDescriptiveRepositoryObserver, AbstractPredictiveSystem):

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
    def get_recommendation(self, user_pk, utc_timestamp):
        pass

    """
    This is the unique identificator. Must be unique between all systems
    """
    @property
    def unique_identificator(self):
        return "predictive.systems.statisticalpredictivesystem"



