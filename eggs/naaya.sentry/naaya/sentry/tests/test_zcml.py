"""Tests for loading naaya.sentry configure.zcml."""

import unittest

from zope.configuration import xmlconfig

import naaya.sentry
from naaya.sentry.handlers import errorRaisedSubscriber


class ZCMLTests(unittest.TestCase):

    def test_subscriber_registered(self):
        # execute=False keeps the global registry untouched for later tests.
        import Products.Five
        context = xmlconfig.file('meta.zcml', Products.Five)
        context = xmlconfig.file('configure.zcml', naaya.sentry,
                                 context=context, execute=False)
        args = [a.get('args') or () for a in context.actions]
        self.assertTrue(any(errorRaisedSubscriber in arg for arg in args))
