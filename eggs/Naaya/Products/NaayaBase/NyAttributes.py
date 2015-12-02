"""
This module contains a class for customizing attribute access.
It is used to provide values for two catalog indexes:

    - B{objectkeywords_I{lang}} where lang is the a language code

    - B{istranslated_I{lang}} where lang is the a language code
"""

from Products.NaayaBase.NyContentType import NyContentType

class NyAttributes:
    """ """

    def get_meta_label(self):
        if isinstance(self, NyContentType):
            return NyContentType.get_meta_label(self)
        elif hasattr(self, 'meta_label'):
            return self.meta_label
        else:
            return self.meta_type

    def __getattr__(self, name):
        """
        Called when an attribute lookup has not found the attribute in the usual places.
        @param name: the attribute name
        @return: should return the attribute value or raise an I{AttributeError} exception.
        """

        # this is for performance reasons
        # it should be updated if/when adding new computed attributes
        if not(name and name[0] in 'oict'):
            raise AttributeError, name

        if name.startswith('objectkeywords_'):
            parts = name.split('_')
            func, lang = parts[0], parts[1]
            return self.objectkeywords(lang)
        elif name.startswith('istranslated_'):
            parts = name.split('_')
            func, lang = parts[0], parts[1]
            return self.istranslated(lang)
        elif name.startswith('coverage_'):
            parts = name.split('_')
            func, lang = parts[0], parts[1]
            return self.getLocalProperty('coverage', lang)
        elif name.startswith('tags_'):
            parts = name.split('_')
            func, lang = parts[0], parts[1]
            return self._tags(lang)
        raise AttributeError, name
