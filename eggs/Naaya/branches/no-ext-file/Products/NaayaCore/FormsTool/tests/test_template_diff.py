from zope.interface import implements, Interface
from zope.component import queryMultiAdapter, adapts
from zope.component import getGlobalSiteManager

from Products.NaayaCore.FormsTool.interfaces import ITemplate, ITemplateSource
from naaya.component.interfaces import IDiff

from Products.Naaya.tests.NaayaTestCase import NaayaTestCase

class ITemplateDemo(Interface):
    """"""

class TemplateDemo(object):
    implements(ITemplateDemo, ITemplate)

    def __init__(self, source):
        self.source = source

    def __call__(self, *args, **kwargs):
        return self.source

class TemplateDemoSource(object):
    adapts(ITemplateDemo)

    def __init__(self, template):
        self.template = template

    def __call__(self):
        return self.template.source

gsm = getGlobalSiteManager()
gsm.registerAdapter(TemplateDemoSource, (ITemplateDemo, ), ITemplateSource)

class TemplateMakeDiffTestCase(NaayaTestCase):
    def setUp(self):
        self.template1 = TemplateDemo('foo')
        self.template2 = TemplateDemo('bar')

    def test_query_diff(self):
        diff = queryMultiAdapter((self.template1, self.template2), IDiff)

        self.assertTrue(diff is not None)
        self.assertEqual(diff.source1, self.template1.source)
        self.assertEqual(diff.source2, self.template2.source)
        self.assertTrue('-foo' in diff.html_diff)
        self.assertTrue('+bar' in diff.html_diff)
