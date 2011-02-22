from sqlalchemy.schema import Table, MetaData, Column, ForeignKey
from sqlalchemy.types import String, Integer, Float
from sqlalchemy.orm import mapper, relation

metadata = MetaData()

country_table = Table('COUNTRY', metadata, 
        Column('CNT_KEY', Integer, primary_key=True),
        Column('CNT_CODE', String),
        Column('CNT_LABEL', Boolean),
)

geozone_table = Table('GEOZONE', metadata, 
        Column('ID', Integer, primary_key=True),
        Column('CNT_CODE', String, ForeignKey(Country.CNT_CODE)),
        Column('GEO_CODE', String),
        Column('GEO_LABEL', String),
)

source_table = Table('SOURCE', metadata, 
        Column('SRC_KEY', Integer, primary_key=True),
        Column('SRC_CODE', String),
        Column('SRC_LABEL', String),
        Column('SRC_URL', String),
)

value_table = Table('VALUE', metadata, 
        Column('VAL_KEY', Integer, primary_key=True),
        Column('VAR_CODE', String),
        Column('VAL_CNT_CODE', String, ForeignKey(Country.CNT_CODE)),
        Column('VAL_GEO_CODE', String),
        Column('VAL_YEAR', Integer),
        Column('VAL', Float),
        Column('VAL_SRC', String),
        Column('VAL_CMT', String),
)

variable_table = Table('VARIABLE', metadata, 
        Column('VAR_KEY', Integer, primary_key=True),
        Column('VAR_CODE', String),
        Column('VAR_LABEL', String),
        Column('VAR_DEF', String),
        Column('VAR_SRC_CODE', String),
        Column('VAR_CODE_SRC', String),
        Column('VAL_UNIT', String),
        Column('VAL_TOPIC', String),
        Column('VAL_CMT', String),
)

class Country(object):
    def __init__(self, **kwargs):
        for k, v in kwargs.iteritems():
            setattr(self, k, v)

class Geozone(object):
    def __init__(self, **kwargs):
        for k, v in kwargs.iteritems():
            setattr(self, k, v)

class Source(object):
    def __init__(self, **kwargs):
        for k, v in kwargs.iteritems():
            setattr(self, k, v)

class Value(object):
    def __init__(self, **kwargs):
        for k, v in kwargs.iteritems():
            setattr(self, k, v)

class Variable(object):
    def __init__(self, **kwargs):
        for k, v in kwargs.iteritems():
            setattr(self, k, v)

mapper(Country, country_table)
mapper(Geozone, geozone_table)
mapper(Source, source_table)
mapper(Value, value_table)
mapper(Variable, variable_table)