
# Zope imports
from zope.interface import implements, Interface
from zope.component import adapts, queryAdapter, getGlobalSiteManager
from OFS.SimpleItem import SimpleItem
from Products.PluginIndexes.FieldIndex.FieldIndex import FieldIndex

# Naaya imports
from Products.Naaya.tests.NaayaTestCase import NaayaTestCase
from Products.NaayaCore.CatalogTool import CatalogTool
from Products.NaayaCore.CatalogTool.interfaces import INyCatalogIndexing

class _ISpecialTestObject(Interface):
    """ mock interface """

def register_index_adapter(adapter):
    """
    Add a mock INyCatalogIndexing for _ISpecialTestObject
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            gsm = getGlobalSiteManager()
            gsm.registerAdapter(adapter, (_ISpecialTestObject,),
                                INyCatalogIndexing)
            try:
                return func(*args, **kwargs)
            finally:
                gsm.unregisterAdapter(adapter, (_ISpecialTestObject,),
                                      INyCatalogIndexing)
        wrapper.func_name = func.func_name
        return wrapper
    return decorator

class _MockObject(SimpleItem):
    implements(_ISpecialTestObject)

    def __init__(self, **kw):
        for (k, v) in kw.items():
            setattr(self, k, v)

class MockAdapter(object):

    def __init__(self, context):
        self.context = context

    def __getattr__(self, name):
        if name in ('testing.purposes', 'testing_purposes'):
            return 'Adapted_value'
        else:
            return getattr(self.context, name)

class CatalogToolTestCase(NaayaTestCase):

    # CatalogTool.patch_zope_catalog_indexing already applied by zca
    # through naaya:call in zcml

    @register_index_adapter(MockAdapter)
    def test_catalogtool_meta_patch(self):
        mo = _MockObject(name='Unadapted', **{'testing.purposes': True})
        cat_tool = CatalogTool.CatalogTool('testcatalog', 'testcatalog')
        # clear meta data schema
        for name in cat_tool._catalog.names:
            cat_tool.delColumn(name)
        cat_tool._catalog.addColumn('testing.purposes')
        cat_tool._catalog.addColumn('name')
        records = cat_tool._catalog.recordify(mo)
        self.assertEqual(('Adapted_value', 'Unadapted'), records)

    @register_index_adapter(MockAdapter)
    def test_catalogtool_meta_patch_in_naaya(self):
        mo = _MockObject(name='Unadapted', **{'testing.purposes': True})
        cat_tool = self.portal.getCatalogTool()
        cat_tool._catalog.addColumn('testing.purposes')
        cat_tool._catalog.addColumn('name')
        records = cat_tool._catalog.recordify(mo)
        self.assertTrue('Unadapted' in records)
        self.assertTrue('Adapted_value' in records)

    def test_catalogtool_meta_no_adapter(self):
        mo = _MockObject(name='Unadapted', **{'testing.purposes': True})
        cat_tool = CatalogTool.CatalogTool('testcatalog', 'testcatalog')
        # clear meta data schema
        for name in cat_tool._catalog.names:
            cat_tool.delColumn(name)
        cat_tool._catalog.addColumn('testing.purposes')
        cat_tool._catalog.addColumn('name')
        records = cat_tool._catalog.recordify(mo)
        self.assertEqual((True, 'Unadapted'), records)

    @register_index_adapter(MockAdapter)
    def test_catalogtool_index_patch(self):
        mo = _MockObject(name='Unadapted', **{'testing_purposes': True})
        fi1 = FieldIndex('testing_purposes')
        fi2 = FieldIndex('name')
        cat_tool = CatalogTool.CatalogTool('testcatalog', 'testcatalog')
        # clear existent indexes
        for name in cat_tool._catalog.indexes.keys():
            cat_tool.delindex(name)
        cat_tool._catalog.addIndex('testing_purposes', fi1)
        cat_tool._catalog.addIndex('name', fi2)
        cataloged = cat_tool._catalog.catalogObject(mo, 'mo_ui')
        self.assertEqual(len(fi1.items()), 1)
        self.assertEqual(len(fi2.items()), 1)
        self.assertEqual((fi1.items()[0][0], fi2.items()[0][0]),
                         ('Adapted_value', 'Unadapted'))

    def test_catalogtool_index_no_adapter(self):
        mo = _MockObject(name='Unadapted', **{'testing_purposes': True})
        fi1 = FieldIndex('testing_purposes')
        fi2 = FieldIndex('name')
        cat_tool = CatalogTool.CatalogTool('testcatalog', 'testcatalog')
        # clear existent indexes
        for name in cat_tool._catalog.indexes.keys():
            cat_tool.delindex(name)
        cat_tool._catalog.addIndex('testing_purposes', fi1)
        cat_tool._catalog.addIndex('name', fi2)
        cataloged = cat_tool._catalog.catalogObject(mo, 'mo_ui')
        self.assertEqual(len(fi1.items()), 1)
        self.assertEqual(len(fi2.items()), 1)
        self.assertEqual((fi1.items()[0][0], fi2.items()[0][0]),
                         (True, 'Unadapted'))
