# -*- coding: utf-8 -*-

from dia.predictive.systems.statistical.system import StatisticalPredictiveSystem

ALL_SYSTEMS = [
    StatisticalPredictiveSystem,
]


def get_predictive_system(unique_identificator):
    for system in ALL_SYSTEMS:
        if system.unique_identificator == unique_identificator:
            return system
    return None
