# -*- coding: utf-8 -*-
import re
from lxml.html.soupparser import fromstring
from unittest import mock

from Products.NaayaCore.managers.session_manager import session_manager
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
            'location': '',
            'geo_type': 'Forest',
            'coverage': 'Australia',
            'groups': [],
            'category-organization':'Forest',
            'category-marketplace':'Forest',
            'category-supporting-solutions':'Forest',
            'topics':['Something Topic'],
            'landscape_type':['Something Landscape'],
        }

    @property
    def session_contents(self):
        # singleton
        if getattr(self, '_session_contents', False):
            return self._session_contents
        d = {}
        for (args, kwargs) in self.portal.REQUEST.SESSION.set.call_args_list:
            d[args[0]] = args[1]
        self._session_contents = d
        return self._session_contents

    def setUp(self):
        super(RegistrationTestCase, self).setUp()
        self.patches = []
        self.patches.append(
            mock.patch('destinet.registration.ui.transaction'))
        # Grant required permissions to Anonymous for registration
        self.portal.manage_permission('Naaya - Create user',
                                       ['Anonymous'], acquire=1)
        self.portal.manage_permission('Naaya - Skip Captcha',
                                       ['Anonymous'], acquire=1)
        self.patches.append(
            mock.patch.object(self.portal.REQUEST, 'HTTP_REFERER',
                  self.portal.absolute_url() + '/create_destinet_account_html'))
        self.patches.append(mock.patch.object(self.portal.REQUEST, 'form', {}))
        ctx = mock.Mock()
        ctx.getSite.return_value = self.portal
        ctx.setSession.side_effect = self.portal.setSession
        ctx.setSessionErrorsTrans.side_effect = self.portal.setSessionErrorsTrans
        ctx.setRequestRoleSession.side_effect = self.portal.setRequestRoleSession
        ctx.absolute_url.return_value = self.portal.absolute_url()
        ctx.name_cookie = '__ac_name'
        ctx.pw_cookie = '__ac_password'
        ctx.REQUEST = self.portal.REQUEST
        session = mock.Mock()
        session.keys.return_value = []
        session.get.return_value = None
        setattr(self.portal.REQUEST, 'SESSION', session)
        self.context = ctx
        self.EMAIL = {}
        def sendCreateAccountEmail(**kw):
            self.EMAIL.update(**kw)
        self.patches.append(mock.patch.object(self.portal, 'sendCreateAccountEmail',
                                              sendCreateAccountEmail))
        for patch in self.patches:
            patch.start()

        # schema for NyContact
        schema = self.portal.portal_schemas['NyContact']
        schema.addWidget('topics', widget_type='SelectMultiple', data_type='list')
        schema.addWidget('target-groups', widget_type='SelectMultiple', data_type='list')
        schema.addWidget('administrative_level', widget_type='Select', data_type='str')
        schema.addWidget('landscape_type', widget_type='SelectMultiple', data_type='list')
        schema['geo_type-property'].required = False
        schema['coverage-property'].required = True

    def tearDown(self):
        for patch in self.patches:
            patch.stop()

    def test_pass_mismatch(self):
        self.portal.REQUEST.form.update(self.initial_data)
        self.portal.REQUEST.form.update(confirm='unequal')
        process_create_account(self.context, self.portal.REQUEST)
        session = self.session_contents
        self.assertIn('The form contains errors', session['site_errors'][0])

    def test_user_created(self):
        self.portal.REQUEST.form.update(self.initial_data)
        process_create_account(self.context, self.portal.REQUEST)
        acl = self.portal.getAuthenticationTool()
        user = acl.getUser('doejohn')
        self.assertTrue(user.email, 'jdoe@eea.europa.eu')

    def test_form(self):
        from unittest import SkipTest
        raise SkipTest('bundles not loaded for test portal')
        self.portal.REQUEST.SESSION = {}
        create_account = self.portal.createaccount_html(self.portal.REQUEST)
        dom = fromstring(re.sub(r'\s+', ' ', create_account))
        h1 = dom.xpath('//h1')
        self.assertEqual(h1[0].text, 'DestiNet account application')
