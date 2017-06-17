# -*- coding: utf-8 -*-

"""
This is the SQL Alchemy implementation of the AbstractDescriptiveRepository
interface.

In the future, this can be implemented for Django and its ORM.
"""

from dia.interfaces import AbstractDescriptiveRepository

from dia.models import GlucoseLevel, Activity, Feeding, InsulinAdministration,\
    Trait
    

import sqlalchemy
import os


"""
Creamos la base de datos en el directorio del módulo
"""
base_dir_list = os.path.abspath(__file__).split('/')[:-1]
base_dir = '/'.join(base_dir_list)

engine = sqlalchemy.create_engine(
    'sqlite:///' + base_dir + '/sqlalchemy.db',
    echo=False,
    poolclass=sqlalchemy.pool.QueuePool,
    pool_size=20,
    max_overflow=100,
)

"""
This returns the session able to interact with the model layer
"""
from sqlalchemy.orm import sessionmaker
Session = sessionmaker(bind=engine)
def session():
    session = Session()
    return session




# MODELOS
################################################################################

from sqlalchemy import Column, Integer, Float
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base(engine)

class SAGlucoseLevel(Base, GlucoseLevel):
    """"""
    __tablename__ = 'descriptive_glucose_levels'

    """"""
    pk = Column(Integer, primary_key=True)
    user_pk = Column(Integer, nullable=False)
    utc_timestamp = Column(Integer, nullable=False, index=True)
    mgdl_level = Column(Float, nullable=False)
    def __str__(self):
        return str(dict(self))


class SAActivity(Base, Activity):
    """"""
    __tablename__ = 'descriptive_activities'

    """"""
    pk = Column(Integer, primary_key=True)
    user_pk = Column(Integer, nullable=False)
    utc_timestamp = Column(Integer, nullable=False, index=True)
    intensity = Column(Integer, nullable=False)
    minutes = Column(Integer, nullable=False)
    def __str__(self):
        return str(dict(self))


class SAFeeding(Base, Feeding):
    """"""
    __tablename__ = 'descriptive_feedings'

    """"""
    pk = Column(Integer, primary_key=True)
    user_pk = Column(Integer, nullable=False)
    utc_timestamp = Column(Integer, nullable=False, index=True)
    total_gr = Column(Float, nullable=False)
    total_ml = Column(Float, nullable=False)
    carb_gr = Column(Float, nullable=False)
    protein_gr = Column(Float, nullable=False)
    fat_gr = Column(Float, nullable=False)
    fiber_gr = Column(Float, nullable=False)
    alcohol_gr = Column(Float, nullable=False)
    def __str__(self):
        return str(dict(self))


class SAInsulinAdministration(Base, InsulinAdministration):
    """"""
    __tablename__ = 'descriptive_insulin_administrations'

    """"""
    pk = Column(Integer, primary_key=True)
    user_pk = Column(Integer, nullable=False)
    utc_timestamp = Column(Integer, nullable=False, index=True)
    insulin_type = Column(Integer, nullable=False)
    insulin_units = Column(Float, nullable=False)
    def __str__(self):
        return str(dict(self))


class SATrait(Base, Trait):
    """"""
    __tablename__ = 'descriptive_trait_changes'

    """"""
    pk = Column(Integer, primary_key=True)
    user_pk = Column(Integer, nullable=False)
    utc_timestamp = Column(Integer, nullable=False, index=True)
    kind = Column(Integer, nullable=False)
    value = Column(Float, nullable=False)
    def __str__(self):
        return str(dict(self))


Base.metadata.create_all(checkfirst=True)
####################################################################


class SQLAlchemyDescriptiveRepository(AbstractDescriptiveRepository):

    def add_glucose_level(self, user_pk=None, utc_timestamp=None, mgdl_level=None):
        s = session()
        glucose = SAGlucoseLevel(user_pk=user_pk, utc_timestamp=utc_timestamp, mgdl_level=mgdl_level)
        s.add(glucose)
        s.commit()
        return glucose

    def get_glucoses(self, user_pk, from_utc_timestamp=None,
        until_utc_timestamp=None, mgdl_level_above=None, mgdl_level_below=None,
        limit=None, order_by_utc_timestamp=True, order_ascending=True):
        
        s = session()
        query = s.query(SAGlucoseLevel)
        query = query.filter(SAGlucoseLevel.user_pk == user_pk)
        
        if from_utc_timestamp:
            query = query.filter(SAGlucoseLevel.utc_timestamp >= from_utc_timestamp)
        if until_utc_timestamp:
            query = query.filter(SAGlucoseLevel.utc_timestamp <= from_utc_timestamp)
        if mgdl_level_above:
            query = query.filter(SAGlucoseLevel.mgdl_level >= mgdl_level_above)
        if mgdl_level_below:
            query = query.filter(SAGlucoseLevel.mgdl_level <= mgdl_level_below)
            
        if order_by_utc_timestamp:
            if order_ascending:
                query = query.order_by(SAGlucoseLevel.utc_timestamp)
            else:
                query = query.order_by(SAGlucoseLevel.utc_timestamp.desc())

        if limit:     
            query = query.limit(limit)
        
        return query.all()

    def add_activity(self, user_pk=None, utc_timestamp=None, intensity=None, minutes=None):
        s = session()
        activity = SAActivity(user_pk=user_pk, utc_timestamp=utc_timestamp, intensity=intensity, minutes=minutes)
        s.add(activity)
        s.commit()
        return activity

    def get_activities(self, user_pk, from_utc_timestamp=None,
        until_utc_timestamp=None, limit=None, order_by_utc_timestamp=True,
        order_ascending=True):
        
        s = session()
        query = s.query(SAActivity)
        query = query.filter(SAActivity.user_pk == user_pk)
        
        if from_utc_timestamp:
            query = query.filter(SAActivity.utc_timestamp >= from_utc_timestamp)
        if until_utc_timestamp:
            query = query.filter(SAActivity.utc_timestamp <= from_utc_timestamp)
            
        if order_by_utc_timestamp:
            if order_ascending:
                query = query.order_by(SAActivity.utc_timestamp)
            else:
                query = query.order_by(SAActivity.utc_timestamp.desc())

        if limit:     
            query = query.limit(limit)
        
        return query.all()
        

    def add_insulin_administration(self, user_pk=None, utc_timestamp=None, insulin_type=None,
        insulin_units=None):
        s = session()
        insulin = SAInsulinAdministration(user_pk=user_pk, utc_timestamp=utc_timestamp, insulin_type=insulin_type, insulin_units=insulin_units)
        s.add(insulin)
        s.commit()
        return insulin

    def get_insulin_administrations(self, user_pk, from_utc_timestamp=None,
        until_utc_timestamp=None, insulin_types_in=None, limit=None,
        order_by_utc_timestamp=True, order_ascending=True):
        
        s = session()
        query = s.query(SAInsulinAdministration)
        query = query.filter(SAInsulinAdministration.user_pk == user_pk)
        
        if from_utc_timestamp:
            query = query.filter(SAInsulinAdministration.utc_timestamp >= from_utc_timestamp)
        if until_utc_timestamp:
            query = query.filter(SAInsulinAdministration.utc_timestamp <= from_utc_timestamp)
            
        if order_by_utc_timestamp:
            if order_ascending:
                query = query.order_by(SAInsulinAdministration.utc_timestamp)
            else:
                query = query.order_by(SAInsulinAdministration.utc_timestamp.desc())
        
        if insulin_types_in:
            query = query.filter(SAInsulinAdministration.insulin_type.in_(insulin_types_in))

        if limit:     
            query = query.limit(limit)
        
        return query.all()


    def add_feeding(self, user_pk=None, utc_timestamp=None, total_gr=0, total_ml=0,
        carb_gr=0, protein_gr=0, fat_gr=0, fiber_gr=0, alcohol_gr=0):
        s = session()
        feeding = SAFeeding(user_pk=user_pk, utc_timestamp=utc_timestamp, \
            total_gr=total_gr, total_ml=total_ml, carb_gr=carb_gr, protein_gr=protein_gr,\
            fat_gr=fat_gr, fiber_gr=fiber_gr, alcohol_gr=alcohol_gr)
        s.add(feeding)
        s.commit()
        return feeding

    def get_feedings(self, user_pk, from_utc_timestamp=None,
        until_utc_timestamp=None, limit=None, order_by_utc_timestamp=True,
        order_ascending=True):

        s = session()
        query = s.query(SAFeeding)
        query = query.filter(SAFeeding.user_pk == user_pk)
        
        if from_utc_timestamp:
            query = query.filter(SAFeeding.utc_timestamp >= from_utc_timestamp)
        if until_utc_timestamp:
            query = query.filter(SAFeeding.utc_timestamp <= from_utc_timestamp)
            
        if order_by_utc_timestamp:
            if order_ascending:
                query = query.order_by(SAFeeding.utc_timestamp)
            else:
                query = query.order_by(SAFeeding.utc_timestamp.desc())

        if limit:     
            query = query.limit(limit)
        
        return query.all()



    def update_trait(self, user_pk=None, utc_timestamp=None, kind=None, value=None):
        s = session()
        trait = SATrait(user_pk=user_pk, utc_timestamp=utc_timestamp, kind=kind, value=value)
        s.add(trait)
        s.commit()
        return trait
    
    """
    get_traits("1", whatever, order_ascending=False, limit=1) nos daria el ultimo
    """
    def get_traits(self, user_pk, kind, from_utc_timestamp=None,
        until_utc_timestamp=None, limit=None, order_by_utc_timestamp=True,
        order_ascending=True):

        s = session()
        query = s.query(SATrait)
        query = query.filter(SATrait.user_pk == user_pk).\
                filter(SATrait.kind == kind)
        
        if from_utc_timestamp:
            query = query.filter(SATrait.utc_timestamp >= from_utc_timestamp)
        if until_utc_timestamp:
            query = query.filter(SATrait.utc_timestamp <= from_utc_timestamp)
            
        if order_by_utc_timestamp:
            if order_ascending:
                query = query.order_by(SATrait.utc_timestamp)
            else:
                query = query.order_by(SATrait.utc_timestamp.desc())

        if limit:     
            query = query.limit(limit)
        
        return query.all()
        
