from datetime import datetime
import xml

from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import view_management_screens
from Acquisition import Implicit
from OFS.SimpleItem import SimpleItem
from DateTime import DateTime
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from zope import interface

from interfaces import IOAIRecord
from utils import process_form, create_object, DT2dt

def manage_addOAIRecord(self, id, **kwargs):
    ob = create_object(self, OAIRecord, id)
    process_form(ob, IOAIRecord, kwargs)
    ob.initialize()

class OAIRecord(SimpleItem, Implicit):
    """ This item is used only with ZCatalog storage type """
    interface.implements(IOAIRecord)

    meta_type = 'Open Archive Record'

    security = ClassSecurityInfo()

    def __getattr__(self, name):
        "Used to provide needed arguments for ZCatalog"
        if name.startswith('h_'):
            if hasattr(self, 'header'):
                return getattr(self.header, name[1:])
        elif name.startswith('m_'):
            if hasattr(self, 'metadata'):
                try:
                    return self.metadata.getField(name[2:])
                except:
                    pass
        else:
            return self.__getattribute__(name)
        raise AttributeError

    security.declarePrivate('initialize')
    def initialize(self):
        """ """
        self.index_object()

    security.declarePrivate('update')
    def update(self, **kw):
        """ """
        process_form(self, IOAIRecord, kw)
        self.last_update = datetime.now()
        self.reindex_object()

    security.declarePrivate('isDeleted')
    def isDeleted(self):
        return self.deleted

    security.declarePrivate('index_object')
    def index_object(self):
        """ """
        try:
            self.getCatalog().catalog_object(self, str('/'.join(
                                                    self.getPhysicalPath())))
        except:
            pass

    security.declarePrivate('unindex_object')
    def unindex_object(self):
        """ """
        self.getCatalog().uncatalog_object(str('/'.join(
                                                self.getPhysicalPath())))

    security.declarePrivate('reindex_object')
    def reindex_object(self):
        """ """
        self.unindex_object()
        self.index_object()

    security.declarePublic('getHarvester')
    def getHarvester(self):
        return self.aq_parent

def before_remove_handler(ob, event):
    ob.unindex_object()

def created_handler(ob, event):
    ob.index_object()

#SQLite storage

class OAIRecordMapper(object):
    """ SQLAlchemy mapper """
    def __init__(self, id, harvester):
        self.id = id
        self.harvester = harvester

    def __repr__(self):
        return '<OAIRecord ' + str(self.id) + '>'

class OAIRecordMapMapper(object):
    """ SQLAlchemy mapper """
    def __init__(self, lang, record_id, key, value):
        self.lang = lang
        self.record_id = record_id
        self.key = key
        self.value = value

    def __repr__(self):
        return '<OAIRecordMap ' + str(self.id) + '>'

class OAIRecordMapFullMapper(object):
    """ SQLAlchemy mapper """
    def __init__(self, lang, record_id, key, value):
        self.lang = lang
        self.record_id = record_id
        self.key = key
        self.value = value

    def __repr__(self):
        return '<OAIRecordFullMap ' + str(self.id) + '>'
