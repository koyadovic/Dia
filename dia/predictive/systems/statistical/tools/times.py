# -*- coding: utf-8 -*-
# from datetime import datetime, time, timedelta
# 
# def time_in_minutes(time):
#     return (time.hour * 60 ) + time.minute
# 
# def absolute_difference_in_minutes(time, time2):
#     return abs(time_in_minutes(time) - time_in_minutes(time2))
# 
# # coge dos parametros, un datetime.time y una lista de objetos datetime.time
# # devuelve de la lista el time más cercano al del primer parámetro
# # esta función es una mierda
# def nearest_time_in_time_list(time, times_list):
#     minutes_time = time_in_minutes(time)
#     if minutes_time < 3 * 60: # Si es menos de las 3:00, suma 24h
#         minutes_time += 24 * 60
#     min_difference = 24 * 60 * 2
#     nearest_time_result = None
#     for t in times_list:
#         difference = absolute_difference_in_minutes(time, t)
#         if difference < min_difference:
#             nearest_time_result = t
#             min_difference = difference
#     return nearest_time_result
