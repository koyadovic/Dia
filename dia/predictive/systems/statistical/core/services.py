# -*- coding: utf-8 -*-
from modules.analysis.tools.context import Context


def get_recommendation(user_id, current_datetime):
    context = Context(user_id, current_datetime)
    recommendation = None # complete_recommendation(context)
    """
    Retorna un objeto Recommendation()
    con los siguientes atributos:

    user_id
    current_datetime
    ch_grams
    insulins
    
    insulins es una lista de diccionarios con las claves: 'type' y 'dose'
    """
    return recommendation
