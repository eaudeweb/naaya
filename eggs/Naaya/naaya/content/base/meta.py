# Python imports
import os
from copy import copy
import types

# Zope imports
from AccessControl import ClassSecurityInfo
from Globals import InitializeClass
from OFS.Application import Application
from OFS.misc_ import Misc_
import zLOG
from zope.interface import Interface
from zope.interface import implements
from zope.configuration.fields import GlobalObject
from zope.app.i18n import ZopeMessageFactory as _

# Products imports
from constants import *
from Products.NaayaBase.NyValidation import NyValidation
from Products.Naaya.NyFolderBase import NyFolderBase
from Products.NaayaCore.SchemaTool.SchemaTool import lookup_schema_product


class INaayaContent(Interface):
    """ Basic Naaya Content """

class INaayaContentDirective(Interface):
    """
    Register a content
    """
    factory = GlobalObject(
        title=_("Factory"),
        description=_("Python name of a factory which can create the"
                      " implementation object.  This must identify an"
                      " object in a module using the full dotted name."),
        required=True,
    )

class NaayaContent(object):
    """ NaayaContent abstract type """
    implements(INaayaContent)
    _contents = {}
    _misc = {}
    _constants = {}

    @property
    def contents(self):
        return self._contents

    @property
    def misc(self):
        return self._misc

    @property
    def constants(self):
        return self._constants

    def __call__(self, key):
        return self._contents.get(key)

def register_naaya_content(_context, factory, **kwargs):
    """ """
    _contents = NaayaContent._contents
    _misc = NaayaContent._misc
    _constants = NaayaContent._constants

    if not factory:
        raise TypeError("No factory provided")

    if isinstance(factory, types.FunctionType):
        factory = factory()
    else:
        return
    _contents[factory['meta_type']] = factory
    _misc.update(factory.get('_misc', {}))

    # register _misc into Zope
    if not Application.misc_.__dict__.has_key('NaayaContent'):
        Application.misc_.__dict__['NaayaContent'] = Misc_('NaayaContent', _misc)
    else:
        Application.misc_.__dict__['NaayaContent'].__dict__['_d'].update(_misc)

    # used by site_header
    _constants['METATYPE_FOLDER'] = 'Naaya Folder'

    security = ClassSecurityInfo()
    NyFolderBase.security = security

    if factory['meta_type'] != 'Naaya Folder' and 'folder_constructors' in factory:

        for folder_property, object_constructor in factory['folder_constructors']:
            setattr(NyFolderBase, folder_property, object_constructor)
            NyFolderBase.security.declareProtected(factory['permission'], folder_property)

    InitializeClass(NyFolderBase)
    # log success
    zLOG.LOG('naaya.content', zLOG.DEBUG, 'Pluggable module "%s" registered' % factory['meta_type'])

def get_schema_name(portal, meta_type):
    if meta_type == 'Naaya Folder':
        return 'NyFolder'

    pluggable = portal.get_pluggable_item(meta_type)
    if pluggable is not None:
        return pluggable['schema_name']

    schema_info = lookup_schema_product(meta_type)
    if schema_info is not None:
        return schema_info['id']

    raise KeyError("No schema_name found for %r in %r" % (meta_type, portal))
