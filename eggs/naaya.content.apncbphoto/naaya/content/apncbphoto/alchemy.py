from sqlalchemy import Column, Integer, String, create_engine, exc
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from naaya.core.zope2util import get_zope_env

Base = declarative_base()

DB_USER = get_zope_env('CONGODB_USER')
DB_PASSWORD = get_zope_env('CONGODB_PASSWORD')
DB_HOST = get_zope_env('CONGODB_HOST')
DB_NAME = get_zope_env('CONGODB_NAME')
DBTEST_NAME = get_zope_env('CONGODBTEST_NAME')


class Document(Base):
    __tablename__ = 'documents'

    docid = Column(Integer, primary_key=True)
    authorid = Column(Integer)
    imageid = Column(Integer)
    subject = Column(String)
    parkid = Column(Integer)
    topic = Column(String)
    ref_geo = Column(String)
    no_collection = Column(String)
    sujet_bref = Column(String)
    esp_nom_com = Column(String)
    esp_nom_lat = Column(String)
    biomeid = Column(Integer)
    vegetationid = Column(Integer)
    paysage = Column(String)
    batiment = Column(String)
    personne = Column(String)
    date = Column(String)
    reference = Column(String)
    ref_id_local = Column(String)
    altitude = Column(String)
    longitude = Column(String)
    latitude = Column(String)


class Author(Base):
    __tablename__ = 'authors'

    authorid = Column(Integer, primary_key=True)
    name = Column(String)
    code = Column(String)


class Image(Base):
    __tablename__ = 'images'

    imageid = Column(Integer, primary_key=True)
    code = Column(String)
    id = Column(String)
    format = Column(String)
    form = Column(String)
    stock = Column(String)


class Park(Base):
    __tablename__ = 'parks'

    parkid = Column(Integer, primary_key=True)
    name = Column(String)
    code = Column(String)


class Biome(Base):
    __tablename__ = 'biomes'

    biomeid = Column(Integer, primary_key=True)
    name = Column(String)


class Vegetation(Base):
    __tablename__ = 'vegetations'

    vegetationid = Column(Integer, primary_key=True)
    name = Column(String)


def get_or_create(session, model, defaults=None, **kwargs):
    instance = session.query(model).filter_by(**kwargs).first()
    if instance:
        return (True, instance)
    else:
        params = dict((k, v) for k, v in kwargs.iteritems())
        params.update(defaults or {})
        instance = model(**params)
        session.add(instance)
        session.commit()
        return (False, instance)


class LookLively(object):
    """Ensures that MySQL connections checked out of the pool are alive."""
    def checkout(self, dbapi_con, con_record, con_proxy):
        try:
            try:
                dbapi_con.ping(False)
            except TypeError:
                dbapi_con.ping()
        except dbapi_con.OperationalError, ex:
            if ex.args[0] in (2006, 2013, 2014, 2045, 2055):
                raise exc.DisconnectionError()
            else:
                raise

engine = create_engine('mysql://' + DB_USER + ':' + DB_PASSWORD + '@' +
                       DB_HOST + '/' + DB_NAME, echo=False, pool_size=20,
                       max_overflow=0, listeners=[LookLively()])
engine.connect()
Session = sessionmaker(bind=engine)

engine_test = create_engine('mysql://' + DB_USER + ':' + DB_PASSWORD + '@' +
                            DB_HOST + '/' + DBTEST_NAME, echo=False,
                            pool_size=20, max_overflow=0,
                            listeners=[LookLively()])
engine_test.connect()
SessionTest = sessionmaker(bind=engine_test)
