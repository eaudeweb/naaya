from Testing import ZopeTestCase

from Acquisition import Implicit
from OFS.SimpleItem import Item

from Products.NaayaBase.NyProperties import NyProperties
from Products.NaayaCore.SchemaTool.Schema import Schema
from Products.NaayaBase.NyContentType import NyContentType, NyContentData
from Products.Naaya.tests.NaayaTestCase import NaayaTestCase
from Products.Naaya.NyFolder import addNyFolder, NyFolder

def _create_test_schema():
    schema = Schema(id='my_schema', title='my_schema')
    # patch the schema instance so we can add widgets
    schema.gl_get_selected_language = lambda: 'en'
    schema.gl_add_languages = lambda a: None
    schema.addWidget('title', widget_type='String', localized=True)
    schema.addWidget('my_str', widget_type='String')
    schema.addWidget('my_local_str', widget_type='String', localized=True)
    schema.addWidget('my_int', widget_type='String', data_type='int')
    return schema

# why do we import from Implicit? don't know; adding it here to make sure we
# test in realistic conditions
class dummy_item(Implicit, NyContentData, NyProperties):
    # _default_language is needed for Localizer to work
    _default_language = 'en'
    def updatePropertiesFromGlossary(self, lang): pass # override with dummy implementation
    def recatalogNyObject(self, arg): pass # override with dummy implementation
    def gl_get_selected_language(self): return self._default_language
    _schema = _create_test_schema()
    def _get_schema(self): return self._schema
    @property
    def aq_base(self):
        return self

class NyDummy(dummy_item, Item, NyContentType):
    # we inherit from Item, because all Naaya content types do so, and this
    # causes problems with the "title" property (and perhaps others)
    pass

class NyContentTypeTestCase(ZopeTestCase.TestCase):
    """ TestCase for NyContentType base class """

    def test_change_schema_properties(self):
        obj = NyDummy()

        obj._change_schema_properties(my_str='asdf')
        self.failUnlessEqual(obj.my_str, 'asdf')

        obj._change_schema_properties(my_local_str='yes')
        obj._change_schema_properties(my_local_str='oui', _lang='fr')
        self.failUnlessEqual(obj.my_local_str, 'yes')
        self.failUnlessEqual(obj.getLocalProperty('my_local_str', 'fr'), 'oui')

    def test_getattr_inheritance(self):
        obj = NyDummy()
        obj._change_schema_properties(my_str='lala_str', my_local_str='lala_local_str')

        self.failUnlessEqual(obj.my_str, 'lala_str')
        self.failUnlessEqual(obj.my_local_str, 'lala_local_str')

        # Note: my_local_str_en is provided by Localizer's LocalPropertyManager
        # class (not by NyContentData), so if we get the correct value,
        # our __getattr__ inheritance works properly
        self.failUnlessEqual(obj.my_local_str_en, 'lala_local_str')
        self.failUnlessRaises(AttributeError, lambda: obj.xzzx)

    def test_special_properties(self):
        """
        we have to treat title (and also id and maybe others) as a special case
        because they are defined as empty strings on the SimpleItem class, so
        NyContentData's __getattr__ method is never called (this breaks
        localized properties)
        """
        obj = NyDummy()
        obj._change_schema_properties(title='tomorrow')
        obj._change_schema_properties(title='demain', _lang='fr')

        self.failUnlessEqual(obj.title, 'tomorrow')
        self.failUnlessEqual(obj.getLocalProperty('title', 'fr'), 'demain')

        # check that things work well even if title is not a local property
        obj._schema = _create_test_schema()
        obj._schema.getWidget('title').localized = False

        obj._change_schema_properties(title='tomorrow')
        obj._change_schema_properties(title='demain', _lang='fr')

        self.failUnlessEqual(obj.title, 'demain')

    def test_copy_schema_properties(self):
        obj = NyDummy()
        obj._change_schema_properties(title='title_val', my_str='my_str_val',
            my_local_str='my_local_str_val', my_int=13)
        obj._change_schema_properties(my_local_str='my_local_str_fr_val',
                                      _lang='fr')

        obj2 = dummy_item()
        obj2.copy_naaya_properties_from(obj)

        self.failUnlessEqual(obj2.title, 'title_val')
        self.failUnlessEqual(obj2.my_str, 'my_str_val')
        self.failUnlessEqual(obj2.my_local_str, 'my_local_str_val')
        self.failUnlessEqual(obj2.getLocalProperty('my_local_str', 'fr'),
                             'my_local_str_fr_val')
        self.failUnlessEqual(obj2.my_int, 13)

    def test_change_schema_properties(self):
        obj = NyDummy()
        obj._change_schema_properties(my_int="12")
        self.failUnlessEqual(obj.my_int, 12)
        self.failUnlessRaises(ValueError, 
                              lambda: obj._change_schema_properties(my_int="3.14"))

    def test_dump_data(self):
        obj = NyDummy()
        obj._change_schema_properties(title='entitle', my_str='somestr',
            my_local_str='enstr', my_int='13', _lang='en')
        obj._change_schema_properties(title='frtitle', my_local_str='frstr', _lang='fr')
        ref_data = {
            'title': {'fr': u'frtitle', 'en': u'entitle'},
            'my_str': u'somestr',
            'my_local_str': {'fr': u'frstr', 'en': u'enstr'},
            'my_int': 13,
        }
        self.assertEqual(dict(obj.dump_data()), ref_data)

class NyContentTypeNaayaTestCase(NaayaTestCase):

    def test_prop_exists(self):
        obj = NyDummy()
        addNyFolder(self.portal, 'my_int')
        self.portal.my_int._setObject('obj_id', obj)
        obj = self.portal.my_int.obj_id

        self.assertTrue(isinstance(obj.my_int, NyFolder))
        self.assertFalse(obj.prop_exists('my_int'))

        obj._change_schema_properties(my_int='33')
        self.assertTrue(obj.prop_exists('my_int'))
