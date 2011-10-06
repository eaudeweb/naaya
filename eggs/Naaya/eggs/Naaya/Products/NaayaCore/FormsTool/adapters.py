from zope.component import getAdapter
from Products.NaayaCore.managers.utils import html_diff

from interfaces import ITemplateSource

class TemplateDiff(object):
    def __init__(self, template1, template2):
        self.source1 = getAdapter(template1, ITemplateSource)()
        self.source2 = getAdapter(template2, ITemplateSource)()

    @property
    def html_diff(self):
        return html_diff(self.source1, self.source2)

class TemplateSource(object):
    def __init__(self, template):
        self.template = template

    def __call__(self):
        return self.template._text
