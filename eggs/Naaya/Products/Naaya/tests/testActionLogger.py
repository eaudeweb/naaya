from unittest import TestCase
import random

from zope import interface
import transaction

from NaayaFunctionalTestCase import NaayaFunctionalTestCase
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

        log_id = self.action_logger.create(message="Some type")
        self.assertEqual(len(self.action_logger), 1)

    def test_add_log_error_type(self):
        self.assertRaises(AssertionError, self.action_logger.append,
                          'Bad type')

    def test_items(self):
        types = ['a', 'b', 'c']
        for i in range(1, 10):
            self.action_logger.create(type=random.choice(types),
                                      message="type")
        for log_id, log in self.action_logger.items(type='a'):
            self.assertEqual(log.type, 'a')

        self.assertEqual(len(self.action_logger.items()),
                         len(self.action_logger))

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
