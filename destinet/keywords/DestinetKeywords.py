try:
    from App.class_init import InitializeClass
except ImportError:
    from Globals import InitializeClass

from zope.publisher.browser import BrowserPage

# Product imports
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Products.NaayaBase.NyContentType import get_schema_helper_for_metatype
from Products.Naaya.constants import *
from Products.NaayaCore.constants import *

tmpl = PageTemplateFile('zpt/site_allocate_keywords', globals())


class allocate_keywords_html(BrowserPage):
    """
    Render the 'allocate keywords' form for selected objects
    """
    def __call__(self, REQUEST):
        context = self.aq_parent
        try:
            ids = REQUEST.form['id']
        except KeyError:
            self.context.setSessionErrorsTrans('No keywords were selected!')
            return self.request.RESPONSE.redirect(context.absolute_url())
        if isinstance(ids, basestring):
            ids = [ids]

        items, schemas, keywords = [], [], []

        for id in ids:
            item = context.getObjectById(id)
            if not item:
                item = context.unrestrictedTraverse(id)
            item_schema = get_schema_helper_for_metatype(context,
                                                         item.meta_type)
            keywords_glossary = getattr(item_schema.schema,
                                        'keywords-property', None)

            if not keywords_glossary:
                raise ValueError("%s meta type does not have keywords-property"
                                 " in schema" % item.meta_type)

            items.append(item)
            schemas.append(item_schema)

            keywords.append(keywords_glossary)

        glossary_id = context.getSite()._getOb('destinet_glossary_id', None)
        if glossary_id:
            glossary = context.getSite()._getOb(glossary_id, None)
        else:
            glossary = None

        options = {
            'here': context,
            'objects': items,
            'schemas': schemas,
            'keywords': keywords,
            'site_glossary': glossary
        }

        return tmpl.__of__(context)(**options)


class allocateKeywords(BrowserPage):
    """
    Update objects' keywords, whether there are bulk keywords selected or
    keywords for each object individually
    """
    def __call__(self, redirect_url='', paths=[], keywords=[], REQUEST=None):
        def split_keywords(text):
            fragments = [f.strip() for f in text.split(',')]
            return set(f for f in fragments if f)

        items = zip(paths, keywords)
        try:
            bulk_action = REQUEST.form['bulk_action']
        except KeyError:
            self.context.setSessionErrorsTrans('No keywords to allocate!')
            return self.request.RESPONSE.redirect(
                self.aq_parent.absolute_url())

        bulk_items = REQUEST.form.get('checked_paths', [])
        bulk_keywords = split_keywords(REQUEST.form['bulk_keywords'])

        for item_path, item_keywords in items:
            item = self.context.unrestrictedTraverse(item_path)
            keywords = split_keywords(item_keywords)

            if item_path in bulk_items:
                for keyword in bulk_keywords:
                    if not keyword.isspace():
                        if keyword not in keywords:
                            if bulk_action == "allocate":
                                keywords.add(keyword)
                        elif bulk_action == "remove":
                            keywords.remove(keyword)
                    else:
                        if keyword in keywords:
                            keywords.remove(keyword)

            keywords = sorted(keywords)
            keywords = ", ".join(keyword for keyword in keywords if keyword)

            site = self.context.getSite()
            item.set_localpropvalue('keywords',
                                    site.gl_get_selected_language(),
                                    keywords)
            item.recatalogNyObject(item)

        self.context.setSessionInfoTrans('Keywords succesfully changed.')
        return self.request.RESPONSE.redirect(redirect_url)
