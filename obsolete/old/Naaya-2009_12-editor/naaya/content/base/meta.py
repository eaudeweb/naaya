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
from Products.Naaya import NyFolder


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
    _misc.update(factory['_misc'])

    # register _misc into Zope
    if not Application.misc_.__dict__.has_key('NaayaContent'):
        Application.misc_.__dict__['NaayaContent'] = Misc_('NaayaContent', _misc)
    else:
        Application.misc_.__dict__['NaayaContent'].__dict__['_d'].update(_misc)

    # used by site_header
    _constants['METATYPE_FOLDER'] = 'Naaya Folder'

    security = ClassSecurityInfo()
    NyFolder.NyFolder.security = security

    if factory['meta_type'] != 'Naaya Folder':

        for folder_property, object_constructor in factory['folder_constructors']:
            setattr(NyFolder.NyFolder, folder_property, object_constructor)
            NyFolder.NyFolder.security.declareProtected(factory['permission'], folder_property)

    InitializeClass(NyFolder.NyFolder)
    # log success
    zLOG.LOG('naaya.content', zLOG.INFO, 'Pluggable module "%s" registered' % factory['meta_type'])

