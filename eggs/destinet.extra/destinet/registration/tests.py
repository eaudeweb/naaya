# -*- coding: utf-8 -*-
import re
from lxml.html.soupparser import fromstring
import mock

from Products.NaayaCore.managers.session_manager import session_manager
from naaya.core.zope2util import path_in_site

from destinet.testing.DestinetTestCase import (DestinetTestCase,
                                               DestinetFunctionalTestCase)
from destinet.registration.constants import (EW_REGISTER_FIELD_NAMES,
                                             WIDGET_NAMES, USER_GROUPS)
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
            mock.patch.object(self.portal.REQUEST, 'HTTP_REFERER',
                  self.portal.absolute_url() + '/create_destinet_account_html'))
        self.patches.append(mock.patch.object(self.portal.REQUEST, 'form', {}))
        ctx = mock.Mock()
        ctx.getSite.return_value = self.portal
        ctx.setSession.side_effect = self.portal.setSession
        session = mock.Mock()
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
        self.assertEqual(session['site_errors'], [u'Password and confirmation do not match'])

    def test_user_created(self):
        self.portal.REQUEST.form.update(self.initial_data)
        process_create_account(self.context, self.portal.REQUEST)
        acl = self.portal.getAuthenticationTool()
        user = acl.getUser('doejohn')
        self.assertTrue(user.email, 'jdoe@eea.europa.eu')

    def test_contact_created(self):
        self.portal.REQUEST.form.update(self.initial_data)
        process_create_account(self.context, self.portal.REQUEST)
        contacts = self.portal['who-who']['destinet-users'].objectValues()
        self.assertTrue(len(contacts), 1)
        contact = contacts[0]
        self.assertEqual(contact.id, 'doejohn')
        path, owner = contact.getOwnerTuple()
        self.assertEqual(owner, 'doejohn')
        self.assertEqual(contact.approved, 1)
        self.assertEqual(contact.lastname, self.initial_data['lastname'])
        self.assertEqual(contact.coverage, self.initial_data['coverage'])
        self.assertEqual(contact.description, self.initial_data['comments'])

    @mock.patch('destinet.registration.core.USER_GROUPS',
                {'test-group': 'resources'})
    def test_contact_with_group(self):
        """ test destinet registration when group is selected """
        self.portal.REQUEST.form.update(self.initial_data)
        self.portal.REQUEST.form.update(groups=['test-group'])
        #import pdb; pdb.set_trace()
        process_create_account(self.context, self.portal.REQUEST)
        contact = self.portal['who-who']['destinet-users'].objectValues()[0]
        pointer = self.portal.resources._getOb(contact.getId())
        self.assertEqual(pointer.pointer, path_in_site(contact))

    def test_form(self):
        from nose.plugins.skip import SkipTest
        raise SkipTest # bundles not loaded for test portal
        self.portal.REQUEST.SESSION = {}
        create_account = self.portal.createaccount_html(self.portal.REQUEST)
        dom = fromstring(re.sub(r'\s+', ' ', create_account))
        h1 = dom.xpath('//h1')
        self.assertEqual(h1[0].text, 'DestiNet account application')
