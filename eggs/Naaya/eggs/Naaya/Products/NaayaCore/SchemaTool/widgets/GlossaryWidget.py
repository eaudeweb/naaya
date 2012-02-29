import simplejson as json

from Globals import InitializeClass
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import view

from Products.NaayaBase.constants import PERMISSION_PUBLISH_OBJECTS
from naaya.core.zope2util import ofs_path

from Widget import WidgetError, manage_addWidget
from StringWidget import StringWidget

def addGlossaryWidget(container, id="", title="Glossary Widget", REQUEST=None, **kwargs):
    """ Contructor for Glossary widget"""
    return manage_addWidget(GlossaryWidget, container, id, title, REQUEST, **kwargs)

class GlossaryWidget(StringWidget):
    """ Glossary Widget """

    security = ClassSecurityInfo()

    meta_type = "Naaya Schema Glossary Widget"
    meta_label = "Glossary"
    _constructors = (addGlossaryWidget,)

    _properties = StringWidget._properties + ({
            'id': 'glossary_id',
            'label': 'Glossary',
            'mode': 'w',
            'type': 'string',
        },
        {
            'id': 'display_mode',
            'label': 'HTML widget type',
            'mode': 'w',
            'type': 'selection',
            'value': 'single_input',
            'select_variable': 'display_mode_options',
        },
        {
            'id': 'separator',
            'label': 'Separator between values',
            'mode': 'w',
            'type': 'string',
        },
        {
            'id':'default',
            'mode':'w',
            'type': 'string',
            'label': 'Default value'
        },
    )

    glossary_id = None
    data_type = 'str'
    separator = ','
    display_mode = 'single-input'
    display_mode_options = ['single-input', 'values-list']

    def _convert_to_form_string(self, value):
        if isinstance(value, basestring):
            return value
        else:
            separator = self.separator
            if not separator.endswith(' '):
                separator += ' '
            return separator.join(value)

    def convert_formvalue_to_pythonvalue(self, value):
        if self.data_type == 'list':
            value = self.splitToList(value, self.separator)

        else:
            if isinstance(value, (list, tuple)):
                value = self.separator.join(v for v in value if v.strip())

        return value

    def convert_to_session(self, value):
        if isinstance(value, (list, tuple)):
            value = self.separator.join(v for v in value if v.strip())
        return value

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'saveProperties')
    def saveProperties(self, REQUEST=None, **kwargs):
        """ Update glossary widget properties"""
        def get_prop(prop):
            return (REQUEST or {}).get(prop, kwargs.get(prop, None))

        self.glossary_id = get_prop('glossary_id')
        if get_prop('display_mode') is not None:
            self.display_mode = get_prop('display_mode')
        if get_prop('separator') is not None:
            self.separator = get_prop('separator')

        if get_prop('all_content_types'):
            for schema in self.getParentNode().getParentNode().objectValues():
                if self.id in schema.objectIds([self.meta_type]):
                    schema._getOb(self.id).glossary_id = self.glossary_id

        return super(GlossaryWidget, self).saveProperties(REQUEST=REQUEST, **kwargs)

    def get_glossary(self):
        site = self.getSite()
        if self.glossary_id in site.objectIds(['Naaya Glossary',
                                               'Naaya Thesaurus']):
            return site._getOb(self.glossary_id)

    security.declareProtected(view, 'search_glossary')
    def search_glossary(self, REQUEST=None, q='', limit=10, lang='en', **kw):
        """ Return json search results based on a query search
        This function is used to return results for js autocomplete

        """

        glossary = self.get_glossary()
        if glossary is None:
            results = []

        elif q == '':
            results = []

        else:
            g_catalog = glossary.getGlossaryCatalog()
            language_name = glossary.get_language_by_code(lang)
            if language_name is None:
                language_name = glossary.get_language_by_code('en')

            def search_catalog(query):
                search_dict = {'approved': 1, language_name: query}
                for brain in g_catalog(**search_dict)[:limit]:
                    ob = brain.getObject()
                    value = ob.get_translation_by_language(language_name)
                    if value:
                        yield value

            results = set()
            results.update(search_catalog('%s*' % q))
            results.update(search_catalog('*%s*' % q))

        return json.dumps(sorted(results))

    security.declareProtected(view, 'glossary_tree')
    def glossary_tree(self, REQUEST=None, lang='en', **kw):
        """ Return all glossary data as a tree. """

        from Products.NaayaGlossary.constants import (
            NAAYAGLOSSARY_FOLDER_METATYPE, NAAYAGLOSSARY_ELEMENT_METATYPE)

        icons_map = {
            'Naaya Glossary': 'glossary',
            'Naaya Glossary Folder': 'folder',
            'Naaya Glossary Element': 'element',
        }
        glossary = self.get_glossary()
        if glossary is None:
            return json.dumps([])

        language_name = glossary.get_language_by_code(lang)

        def recursive_tree(ob):
            icon_url = '/misc_/NaayaGlossary/%s.gif' % icons_map[ob.meta_type]

            kids = ob.objectValues([NAAYAGLOSSARY_FOLDER_METATYPE,
                                    NAAYAGLOSSARY_ELEMENT_METATYPE])
            kids = sorted(kids, key=lambda ob: ob.getId())
            children = [recursive_tree(kid) for kid in kids if kid.approved]

            translation_missing = ''
            if ob is glossary:
                translation = None
                title = ob.title_or_id()
                definition = ofs_path(ob)

            else:
                translation = ob.get_translation_by_language(language_name)
                if translation:
                    title = translation
                else:
                    translation = None
                    title = ob.get_translation_by_language('English')
                    if not title:
                        title = ob.title_or_id()

                    translation_missing = (' <span class="glossary-translation-missing">(' +
                              language_name + ' translation missing)</span>')
                definition = ob.get_def_trans_by_language(language_name)

            insertable = (ob.meta_type != NAAYAGLOSSARY_FOLDER_METATYPE
                or glossary.parent_anchors)

            tree_item = {
                'attributes': {
                    'title': definition,
                    'type': icons_map.get(ob.meta_type),
                },
                'data': {
                    'title': title + translation_missing,
                    'icon': icon_url,
                },
                'children': children,
            }

            if ob is glossary:
                tree_item['state'] = 'open'
            else:
                tree_item['attributes']['glossary-translation'] = (
                    translation or title)
                if insertable:
                    tree_item['attributes']['rel'] = 'insertable'

            return tree_item

        return json.dumps(recursive_tree(glossary))


    template = PageTemplateFile('../zpt/property_widget_glossary', globals())

    admin_html = PageTemplateFile('../zpt/admin_schema_property_glossary', globals())
    admin_html.parent_template = StringWidget.admin_html

InitializeClass(GlossaryWidget)
