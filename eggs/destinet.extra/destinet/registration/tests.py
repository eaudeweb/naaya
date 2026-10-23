# -*- coding: utf-8 -*-
import re
from lxml.html.soupparser import fromstring
from unittest import mock

import transaction
from zope.interface import alsoProvides

from Products.NaayaCore.managers.session_manager import session_manager
from destinet.testing.DestinetTestCase import (DestinetTestCase,
                                               DestinetFunctionalTestCase)
from destinet.registration.constants import (EW_REGISTER_FIELD_NAMES,
                                             WIDGET_NAMES)
from destinet.registration.ui import process_create_account
from destinet.extra.interfaces import IDestinetSite

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
        with mock.patch.object(self.portal, 'admin_addroles') as addroles:
            process_create_account(self.context, self.portal.REQUEST)
        user = self.portal.getAuthenticationTool().getUser('doejohn')
        self.assertEqual(user.email, 'jdoe@eea.europa.eu')
        self.assertEqual(user.firstname, 'John')
        self.assertEqual(user.lastname, 'Døe')
        addroles.assert_called_once_with(['doejohn'], ['Contributor'], '',
                                         send_mail=True)
        self.assertEqual(self.portal.REQUEST.RESPONSE.getHeader('location'),
                         self.portal.absolute_url() + '/login_html')
        self.assertEqual(self.session_contents['title'], 'John Døe')

    def test_user_created_redirects_to_came_from(self):
        self.portal.REQUEST.SESSION.get.side_effect = (
            lambda key, default=None: 'http://localhost/back'
            if key == 'came_from' else default)
        self.portal.REQUEST.form.update(self.initial_data)
        with mock.patch.object(self.portal, 'admin_addroles') as addroles:
            process_create_account(self.context, self.portal.REQUEST)
        self.assertEqual(self.portal.REQUEST.RESPONSE.getHeader('location'),
                         'http://localhost/back')
        addroles.assert_called_once()

    def test_invalid_username_and_email(self):
        self.portal.REQUEST.form.update(self.initial_data)
        self.portal.REQUEST.form.update(username='doe john', email='nope')
        with mock.patch.object(self.portal, 'admin_addroles') as addroles:
            process_create_account(self.context, self.portal.REQUEST)
        addroles.assert_not_called()
        self.assertIsNone(
            self.portal.getAuthenticationTool().getUser('doe john'))
        self.assertEqual(self.session_contents['email-errors'],
                         'Invalid email address')
        self.assertEqual(self.portal.REQUEST.RESPONSE.getHeader('location'),
                         self.portal.absolute_url() +
                         '/create_destinet_account_html')

    def test_existing_username_gets_no_role(self):
        self.portal.getAuthenticationTool().manage_addUser(
            name='doejohn', password='other', confirm='other', roles=[],
            domains=[], firstname='Other', lastname='User',
            email='other@example.com', strict=0)
        self.portal.REQUEST.form.update(self.initial_data)
        with mock.patch.object(self.portal, 'admin_addroles') as addroles:
            process_create_account(self.context, self.portal.REQUEST)
        addroles.assert_not_called()

    def test_failed_signup_gets_no_role(self):
        self.portal.manage_permission('Naaya - Create user', [], acquire=0)
        self.portal.REQUEST.form.update(self.initial_data)
        with mock.patch.object(self.portal, 'admin_addroles') as addroles:
            process_create_account(self.context, self.portal.REQUEST)
        addroles.assert_not_called()
        self.assertIsNone(self.portal.getAuthenticationTool().getUser('doejohn'))



class RegistrationFormTestCase(DestinetFunctionalTestCase):

    def setUp(self):
        super(RegistrationFormTestCase, self).setUp()
        alsoProvides(self.portal, IDestinetSite)
        schema = self.portal.portal_schemas['NyContact']
        schema.addWidget('topics', widget_type='SelectMultiple',
                         data_type='list')
        schema.addWidget('administrative_level', widget_type='Select',
                         data_type='str')
        schema.addWidget('landscape_type', widget_type='SelectMultiple',
                         data_type='list')
        transaction.commit()

    def test_form(self):
        self.browser.go(self.portal.absolute_url() +
                        '/create_destinet_account_html')
        self.assertEqual(self.browser.get_code(), 200,
                         self.browser.get_html()[-3000:])
        dom =fromstring(re.sub(r'\s+', ' ', self.browser.get_html()))
        self.assertEqual(dom.xpath('//h1')[0].text,
                         'Tourism 2030 account application')
        form = dom.xpath('//form[@id="create-account"]')[0]
        self.assertTrue(form.get('action').endswith(
            '/processRequestDestinetRoleForm'))
        names = set(form.xpath('.//*[@name]/@name'))
        for name in ('username:utf8:string', 'email:utf8:string',
                     'password:utf8:string', 'confirm:utf8:string'):
            self.assertIn(name, names)
