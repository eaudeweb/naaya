# -*- coding: utf-8 -*-
import re
from lxml.html.soupparser import fromstring
import mock

from destinet.testing.DestinetTestCase import (DestinetTestCase,
                                               DestinetFunctionalTestCase)
from destinet.registration.constants import (EW_REGISTER_FIELD_NAMES,
                                             WIDGET_NAMES)
from destinet.registration.ui import process_create_account

class RegistrationTestCase(DestinetTestCase):

    initial_data = {
            'username': 'doejohn',
            'firstname': 'John',
            'lastname': u'Døe',
            'email': 'jdoe@eea.europa.eu',
            'password': 'secret',
            'confirm': 'secret',
            'organisation': 'EEA',
            'comments': 'I am John Doe',
            'location': ''
        }

    def setUp(self):
        super(RegistrationTestCase, self).setUp()
        self.patches = []
        self.patches.append(
            mock.patch.object(self.portal.REQUEST, 'HTTP_REFERER',
                             self.portal.absolute_url() + '/create_destinet_account_html'))
        self.patches.append(mock.patch.object(self.portal.REQUEST, 'form', {}))
        self.SESSION = {}
        ctx = mock.Mock()
        ctx.getSite.return_value = self.portal
        def setSession(key, value):
            self.SESSION[key] = value
        ctx.setSession.side_effect = setSession
        self.context = ctx
        self.patches.append(mock.patch.object(self.portal, 'setSession', setSession))
        self.patches.append(
            mock.patch.object(self.portal, 'setSessionErrorsTrans',
                              lambda x: setSession('site_errors', x)))
        self.EMAIL = {}
        def sendCreateAccountEmail(**kw):
            self.EMAIL.update(**kw)
        self.patches.append(mock.patch.object(self.portal, 'sendCreateAccountEmail',
                                              sendCreateAccountEmail))
        for patch in self.patches:
            patch.start()

    def tearDown(self):
        for patch in self.patches:
            patch.stop()

    def test_pass_mismatch(self):
        self.portal.REQUEST.form.update(self.initial_data)
        self.portal.REQUEST.form.update(confirm='unequal')
        process_create_account(self.context, self.portal.REQUEST)
        self.assertEqual(self.SESSION, {'site_errors': u'Password and confirmation do not match'})

    def test_pass_mismatch2(self):
        self.portal.REQUEST.form.update(self.initial_data)
        process_create_account(self.context, self.portal.REQUEST)

    def test_form(self):
        self.portal.REQUEST.SESSION = {}
        create_account = self.portal.createaccount_html(self.portal.REQUEST)
        dom = fromstring(re.sub(r'\s+', ' ', create_account))
        h1 = dom.xpath('//h1')
        self.assertEqual(h1[0].text, 'DestiNet account application')