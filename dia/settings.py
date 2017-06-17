# -*- coding: utf-8 -*-
from predictive.systems.statisticalv2.system import StatisticalV2PredictiveSystem
from descriptive_repository.sqlalchemy_repository import SQLAlchemyDescriptiveRepository

"""
Subclasses of AbstractPredictiveSystem
"""
PREDICTIVE_SYSTEMS = [
    StatisticalV2PredictiveSystem
]


"""
Subclass of AbstractDescriptiveRepository
"""
DESCRIPTIVE_REPOSITORY = SQLAlchemyDescriptiveRepository