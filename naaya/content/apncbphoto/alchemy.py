from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from naaya.core.zope2util import get_zope_env

Base = declarative_base()

DB_USER = get_zope_env('CONGODB_USER')
DB_PASSWORD = get_zope_env('CONGODB_PASSWORD')
DB_HOST = get_zope_env('CONGODB_HOST')
DB_NAME = get_zope_env('CONGODB_NAME')
UPLOAD_DIR = get_zope_env('CONGODB_UPLOAD_DIR')


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
        return instance
    else:
        params = dict((k, v) for k, v in kwargs.iteritems())
        params.update(defaults or {})
        instance = model(**params)
        session.add(instance)
        return instance

engine = create_engine('mysql://' + DB_USER + ':' + DB_PASSWORD + '@' +
                       DB_HOST + '/' + DB_NAME, echo=False)
engine.connect()
Session = sessionmaker(bind=engine)

session = Session()
