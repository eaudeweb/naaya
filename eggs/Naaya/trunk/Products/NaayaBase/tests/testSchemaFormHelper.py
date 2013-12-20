from unittest import TestCase
from mock import Mock

from Products.NaayaBase.NyContentType import SchemaFormHelper

class SchemaFormHelperDefaultCoverageTestCase(TestCase):
    def setUp(self):
        self.widget = Mock()
        self.widget.getDataType = Mock(return_value=str)
        self.widget.default = None
        self.schema = Mock()
        self.schema.getWidget = Mock(return_value=self.widget)
        self.context = Mock()
        self.context.default_geographical_coverage = 'test_coverage'
        self.context.getSession = Mock(return_value=None)

    def test_coverage_value_for_add(self):
        form_helper = SchemaFormHelper(self.schema, self.context)
        value = form_helper._get_value('coverage', add=True)

        self.assertEqual(value, 'test_coverage')

    def test_coverage_value_for_edit(self):
        form_helper = SchemaFormHelper(self.schema, self.context)
        value = form_helper._get_value('coverage', add=False)

        self.assertEqual(value, '')
