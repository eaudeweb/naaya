from unittest import TestCase

from zope import interface
import transaction

from .NaayaFunctionalTestCase import NaayaFunctionalTestCase
from Products.Naaya.action_logger import ActionLogger, ActionLogItem
from Products.Naaya.interfaces import IActionLogger
from Products.Naaya.NyFolder import addNyFolder

class ActionLoggerTest(TestCase):
    """ Basic unittest """
    def setUp(self):
        self.action_logger = ActionLogger()

    def test_add_log(self):
        """ Add a log using action logger api """

        action_log = ActionLogItem(message="Some message")
        log_id = self.action_logger.append(action_log)
        self.assertEqual({log_id: action_log}, dict(self.action_logger))

    def test_add_log_convenience(self):
        """ Add a log using a convenience method """

        log_id = self.action_logger.create(type='x', message="Some type")
        self.assertEqual(len(self.action_logger), 1)
        log = self.action_logger[log_id]
        self.assertEqual((log.type, log.message), ('x', "Some type"))

    def test_add_log_error_type(self):
        self.assertRaises(AssertionError, self.action_logger.append,
                          'Bad type')

    def test_items(self):
        for log_type in ['a', 'b', 'a', 'c', 'a']:
            self.action_logger.create(type=log_type, message="type")
        a_items = list(self.action_logger.items(type='a'))
        self.assertEqual(len(a_items), 3)
        for log_id, log in a_items:
            self.assertEqual(log.type, 'a')

        self.assertEqual(len(self.action_logger.items()), 5)

    def test_remove_log(self):
        log_id = self.action_logger.create(type="Some type")
        del self.action_logger[log_id]
        self.assertEqual(dict(self.action_logger), {})

class ActionLoggerFunctionalTest(NaayaFunctionalTestCase):
    """ Test add remove objects """

    def test_has_action_logger(self):
        """ See if the portal has an action logger and it implements the right
        interface"""
        action_logger = self.portal.getActionLogger()
        assert IActionLogger in interface.providedBy(action_logger)

    def test_template_reads_log_items(self):
        """ Restricted template code can read the attributes of log items """
        from Products.PageTemplates.ZopePageTemplate import (
            manage_addPageTemplate)
        log_id = self.portal.getActionLogger().create(type='role_request',
                                                      message='Hello ș')
        manage_addPageTemplate(self.portal, 'show_log', text=(
            '<p tal:content="string:${options/log/type}: '
            '${options/log/message}" />'))
        log = self.portal.getActionLogger()[log_id]
        self.assertEqual(self.portal.show_log(log=log).strip(),
                         '<p>role_request: Hello ș</p>')
