# -*- coding: utf-8 -*-

"""
Creamos la base de datos en el directorio del módulo
"""
import os
base_dir_list = os.path.abspath(__file__).split('/')[:-1]
base_dir = '/'.join(base_dir_list)
from sqlalchemy.pool import QueuePool
from sqlalchemy import create_engine

engine = create_engine(
    'sqlite:///' + base_dir + '/analysis.db',
    echo=False,
    poolclass=QueuePool,
    pool_size=20,
    max_overflow=100,
)

"""
This returns the session able to interact with the model layer
"""
from sqlalchemy.orm import sessionmaker
Session = sessionmaker(bind=engine)
def analysis_session():
    session = Session()
    return session



