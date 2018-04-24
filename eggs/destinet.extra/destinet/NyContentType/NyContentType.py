import importlib
from lxml.html import fromstring


def initialize(context):
    source = 'Products.NaayaBase.NyContentType'
    NyContentType = importlib.import_module(source).NyContentType
    NyContentType.get_card_src = get_card_src


def get_card_src(self, REQUEST=None, **kw):
    """ """
    for lang in self.gl_get_languages():
        desc = self.getLocalProperty('description', lang)
        if desc:
            tree = fromstring(desc)
            card = tree.find_class('card')
            if card:
                for el in card[0].iterdescendants():
                    if el.tag == 'img':
                        if el.xpath('//img/@src'):
                            return el.xpath('//img/@src')[0]
            break
