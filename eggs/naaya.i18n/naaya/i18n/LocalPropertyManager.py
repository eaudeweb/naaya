# -*- coding: UTF-8 -*-

from time import time

from AccessControl import ClassSecurityInfo
from Globals import InitializeClass
from ExtensionClass import Base
from zope.deprecation import deprecate

from patches import get_request, get_i18n_context
from NyNegotiator import NyNegotiator
from LanguageManagers import get_iso639_name

class LocalAttribute(Base):
    """
    Provides a way to override class variables, useful for example
    for title (defined in SimpleItem).
    """

    def __init__(self, id):
        self.id = id

    def __of__(self, parent):
        return parent.getLocalAttribute(self.id)

# XXX
# For backwards compatibility
# (localizer <= 0.8.0): other classes import 'LocalProperty'
LocalProperty = LocalAttribute

def requires_localproperty(obj, name):
    """

    Returns True if LocalAttribute needs to be set on instance
    to override any class or superclass variables
    that are neither LocalAttribute, nor ForceGetattr.

    """
    try:
        attr_value = getattr(obj.__class__, name)
    except AttributeError:
        # if no such attribute, no need to override
        return False
    else:
        # cross import issue
        from Products.NaayaBase.NyContentType import ForceGetattr
        return not isinstance(attr_value, (LocalProperty, ForceGetattr))


class LocalPropertyManager(object):
    """
    Mixin class that allows to manage localized properties.
    Somewhat similar to OFS.PropertyManager.
    """

    security = ClassSecurityInfo()

    # Metadata for local properties
    # Example: ({'id': 'title', 'type': 'string'},)
    _local_properties_metadata = ()

    # Local properties are stored here
    # Example: {'title': {'en': ('Title', timestamp), 'es': ('Títul', timestamp)}}
    _local_properties = {}

    # OBS!: _local_properties* will be saved on instance when first changed


    security.declarePublic('hasLocalProperty')
    def hasLocalProperty(self, id):
        """Return true if object has a property 'id' (it's present in
        _local_properties_metadata)"""
        for property in self._local_properties_metadata:
            if property['id'] == id:
                return True
        return False

    security.declareProtected('Manage properties', 'set_localpropvalue')
    def set_localpropvalue(self, id, lang, value):
        """
        Sets value in a given lang for a given property name (id).
        If property does not exist (it's not present in
        _local_properties_metadata), then create it with type 'string'

        """
        # Get previous value
        old_value = self.getLocalAttribute(id, lang)
        # Update value only if it is different or new
        if not self.hasLocalProperty(id):
            self.set_localproperty(id, 'string', lang, value)
        elif value != old_value:
            properties = self._local_properties.copy()
            if not properties.has_key(id):
                properties[id] = {}

            properties[id][lang] = (value, time())

            self._local_properties = properties

    security.declareProtected('Manage properties', 'set_localproperty')
    def set_localproperty(self, id, type, lang=None, value=None):
        """
        Adds a new local property. If both `lang` and `value` are supplied,
        then the corresponding value is also set. Otherwise, the property
        will behave like a blank string in usage.
        """
        #  adds type and id to _local_properties_metadata
        if not self.hasLocalProperty(id):
            self._local_properties_metadata += ({'id': id, 'type': type},)
            if requires_localproperty(self, id):
                setattr(self, id, LocalProperty(id))

        # adds value for lang only if lang is not None and value is not None
        if lang is not None:
            self.set_localpropvalue(id, lang, value)

    security.declareProtected('Manage properties', 'del_localproperty')
    def del_localproperty(self, id):
        """Deletes a property"""
        # Update properties metadata
        p = [ x for x in self._local_properties_metadata if x['id'] != id ]
        self._local_properties_metadata = tuple(p)

        # delete attribute
        try:
            del self._local_properties[id]
        except KeyError:
            pass

        try:
            delattr(self, id)
        except AttributeError:
            pass

    # XXX Backwards compatibility
    _setLocalPropValue = set_localpropvalue
    _setLocalProperty = set_localproperty
    _delLocalProperty = del_localproperty

    security.declarePublic('getLocalProperties')
    def getLocalProperties(self):
        """Returns a copy of the properties metadata."""
        return tuple([ x.copy() for x in self._local_properties_metadata ])

    def _getValue(self, idName, lang):
        value = self._local_properties[idName][lang]
        if isinstance(value, tuple): # (value, timestamp)
            return value[0]
        else:
            return value

    security.declarePublic('getLocalAttribute')
    def getLocalAttribute(self, id, lang=None, langFallback=False):
        """Returns a local property
        Note that langFallback is fallback to the bitter end - it will both try
        to find a non default language present and yet other languages
        if the one it found had empty values."""
        if id not in self._local_properties:
            return ''
        # No language, look for the first non-empty available version or def.
        if lang is None:
            request = get_request()
            i18n = get_i18n_context()
            if i18n is None: # didn't traverse any portal yet, e.g. zmi root
                lang = 'en'
            else:
                neg = NyNegotiator()
                # need to negotiate lang based on available langs for this prop.
                lang = neg.getLanguage(self._local_properties[id].keys(),
                                       request, fallback=langFallback)
            if lang is None:
                # eg: we ask default (en), id has only 'de', lang is then None
                # because fallback=False (or else it would have been `de`)
                if i18n['default_language'] in self._local_properties[id]:
                    lang = i18n['default_language']
                else:
                    lang = 'en'

        if lang not in self._local_properties[id]:
            return ''

        value = self._getValue(id, lang)
        # perhaps we found a non default language but the values there are empty
        # TODO: do we really want such aggressive behaviour?
        # what if the client wants empty value for some languages?
        if langFallback and not value:
            for ln in self._local_properties[id]:
                value = self._getValue(id, ln)
                if value:
                    break
        return value


    # XXX For backwards compatibility (<= 0.8.0)
    getLocalProperty = getLocalAttribute

    def __getattr__(self, name):
        try:
            index = name.rfind('_')
            id, lang = name[:index], name[index+1:]
            property = self._local_properties[id]
        except:
            raise AttributeError, "%s instance has no attribute '%s'" \
                                  % (self.__class__.__name__, name)

        return self.getLocalAttribute(id, lang)

    security.declarePublic('get_selected_language')
    #@deprecate(("Calling language related methods on objects is deprecated."
    #            " Call them on NySite_instance.getPortalI18n() instead"))
    def get_selected_language(self):
        """ """
        return get_i18n_context()['selected_language']


    ### For compatibility with old property manager - for here/get_lang..
    security.declarePublic('get_languages_mapping')
    @deprecate(("Calling language related methods like `get_languages_mapping`"
                " on objects is deprecated."
                " Call them on NySite_instance.getPortalI18n() instead"))
    def get_languages_mapping(self):
        """ """
        return get_i18n_context()['languages_mapping']

    security.declarePublic('get_language_name')
    @deprecate(("Calling language related methods like `get_language_name`"
                " on objects is deprecated."
                " Call them on NySite_instance.getPortalI18n() instead"))
    def get_language_name(self, lang):
        """
        Deprecated: Use gl_get_language_name on NySite or even better,
        use get_language_name on getPortalI18n().get_lang_manager()
        This deprecated version can not return custom named languages

        """
        return get_iso639_name(lang)


InitializeClass(LocalPropertyManager)
