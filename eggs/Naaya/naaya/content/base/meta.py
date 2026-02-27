import os

import logging
from AccessControl import ClassSecurityInfo
from AccessControl.class_init import InitializeClass
from OFS.Application import Application
from OFS.misc_ import Misc_
from zope.interface import Interface
from zope.interface import implementer
from zope.configuration.fields import GlobalObject
from zope.i18nmessageid import MessageFactory
_ = MessageFactory('zope')

from .constants import *
from Products.Naaya.NyFolderBase import NyFolderBase
from Products.NaayaCore.SchemaTool.SchemaTool import lookup_schema_product
from Products.NaayaCore.FormsTool.NaayaTemplate import NaayaPageTemplateFile

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

@implementer(INaayaContent)
class NaayaContent(object):
    """ NaayaContent abstract type """
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
    """ Register a naaya content type.

    This is called for each content type using it's config dictionary. This will
    validate the config of the content type, perform a few sanity checks,
    declare the permissions for the content type and register the templates.

    """

    assert factory, "No factory provided"
    assert callable(factory), "Factory must be callable"
    config = factory()

    assert 'meta_type' in config, "Config must contain at least a meta_type"

    _contents = NaayaContent._contents
    _misc = NaayaContent._misc
    _constants = NaayaContent._constants

    _contents[config['meta_type']] = config
    _misc.update(config.get('_misc', {}))

    # register _misc into Zope
    if not hasattr(Application.misc_, 'NaayaContent'):
        setattr(Application.misc_, 'NaayaContent', Misc_('NaayaContent',
                _misc))
    else:
        getattr(Application.misc_, 'NaayaContent').__dict__['_d'].update(_misc)

    # used by site_header
    _constants['METATYPE_FOLDER'] = 'Naaya Folder'

    security = ClassSecurityInfo()
    NyFolderBase.security = security

    # declare permissions for object constructors
    if (config['meta_type'] != 'Naaya Folder' and
        'folder_constructors' in config):
        for folder_property, object_constructor in config['folder_constructors']:
            setattr(NyFolderBase, folder_property, object_constructor)
            NyFolderBase.security.declareProtected(config['permission'],
                    folder_property)
    # register forms
    for form in config.get('forms', []):
        NaayaPageTemplateFile(os.path.join(config['package_path'], 'zpt', form),
                globals(), form)

    InitializeClass(NyFolderBase)
    # log success
    logging.getLogger('naaya.content').warning('Pluggable content type "%s" registered' % config['meta_type'])

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
