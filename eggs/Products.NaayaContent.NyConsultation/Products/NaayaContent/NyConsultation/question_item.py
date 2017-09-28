#Zope imports
from Acquisition import Implicit

#Product imports
from naaya.i18n.LocalPropertyManager import LocalProperty
from Products.NaayaBase.NyProperties import NyProperties


class question_item(Implicit, NyProperties):
    
    body = LocalProperty('body')
    
    def __init__(self, body, lang, sortorder=100):
        self.save_properties(body, lang, sortorder)
        NyProperties.__init__(self)

    def save_properties(self, body, lang, sortorder=100):
        self._setLocalPropValue('body', lang, body)
        try: self.sortorder = int(sortorder)
        except ValueError: self.sortorder = 100

    def set_sortorder(self, sortorder):
        self.sortorder = sortorder

    def get_body(self, lang):
        """ Returns the body string for the given language """
        return self.getLocalProperty('body', lang)

    def get_sortorder(self):
        """ """
        return self.sortorder
