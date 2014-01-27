from zope.interface import implements
from Products.PageTemplates.PageTemplate import PageTemplate
from Products.PageTemplates.PageTemplateFile import PageTemplateFile

from naaya.component import bundles

from interfaces import ITemplate, INaayaPageTemplateFile

class NaayaPageTemplateFile(PageTemplateFile):
    implements(INaayaPageTemplateFile, ITemplate)

    def __init__(self, filename, _globals, name, bundle_name="Naaya"):
        PageTemplateFile.__init__(self, filename, _globals, __name__=name)

        #Register this template to a specific bundle
        bundle = bundles.get(bundle_name)
        bundle.registerUtility(self, ITemplate, name)
        self._bundle_name = bundle_name

    def __of__(self, parent):
        """
        When this NaayaPageTemplateFile is placed in an acquisition context,
        we do our magic: look up the correct (perhaps customized) template
        and return that instead of ourselves.
        """

        try:
            site = parent.getSite()
        except AttributeError, e:
            sm = bundles.get(self._bundle_name)
        else:
            sm = site.getSiteManager()

        form = sm.getUtility(ITemplate, self.__name__)
        if form is self:
            return PageTemplateFile.__of__(self, parent)
        else:
            return form.__of__(parent)
