# -*- coding: utf-8 -*-
from predictive.systems.statistical.system import StatisticalPredictiveSystem
from predictive.systems.statisticalv2.system import StatisticalV2PredictiveSystem

"""
Subclasses of AbstractPredictiveSystem
"""
PREDICTIVE_SYSTEMS = [
    StatisticalPredictiveSystem,
    StatisticalV2PredictiveSystem
]


"""
Subclass of AbstractDescriptiveRepository
"""
DESCRIPTIVE_REPOSITORY = None