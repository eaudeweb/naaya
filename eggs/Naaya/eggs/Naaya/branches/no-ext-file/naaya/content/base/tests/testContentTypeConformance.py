from urllib import quote
from StringIO import StringIO
from random import random
from Testing import ZopeTestCase
import transaction

from zope.component import adapter, getGlobalSiteManager

from Products.Naaya.tests.NaayaFunctionalTestCase import NaayaFunctionalTestCase
from Products.NaayaBase.NyContentType import NyContentData
from naaya.content.base.discover import get_pluggable_content
from naaya.content.base.interfaces import (INyContentObjectAddEvent,
        INyContentObjectEditEvent, INyContentObjectApproveEvent,
        INyContentObjectUnapproveEvent, INyContentObjectMovedEvent)

SCHEMA_TESTABLES = ['contact_item', 'document_item', 'event_item',
                    'exfile_item', 'file_item', 'geopoint_item',
                    'news_item', 'pointer_item', 'story_item', 'url_item']

DYNAMIC_PROPERTIES_TESTABLES =['contact_item', 'document_item', 'event_item',
                               'file_item', 'news_item', 'pointer_item',
                               'story_item', 'url_item']

FORM_TESTABLES = ['contact_item', 'document_item', 'event_item',
                  'exfile_item', 'file_item', 'geopoint_item',
                  'news_item', 'pointer_item', 'story_item', 'url_item']

TRANSLATE_TESTABLES = ['contact_item', 'document_item', 'event_item',
                  'exfile_item', 'file_item', 'geopoint_item',
                  'news_item', 'pointer_item', 'story_item', 'url_item']

INSTALL_UNINSTALL_TESTABLES = ['Naaya News', 'Naaya Story', 'Naaya Blob File',
    'Naaya URL', 'Naaya Extended File', 'Naaya Document', 'Naaya Pointer',
    'Naaya Media File', 'Naaya Event', 'Naaya TalkBack Consultation',
    'Naaya File', 'Naaya GeoPoint']


def _list_content_types():
    for content_type in get_pluggable_content().values():
        if content_type.get('_class', None) is None:
            continue
        yield content_type
content_types = list(_list_content_types())

def _fill_specific_form_fields(form, type_name):
        if type_name == 'NyURL':
            form['redirect:boolean'] = []
        elif type_name == 'NyGeoPoint':
            form['geo_location.lon:utf8:ustring'] = '12.587142'
            form['geo_location.lat:utf8:ustring'] = '55.681004'
        elif type_name == 'NyMediaFile':
            form.find_control('file').add_file(StringIO('the_FLV_data'),
                filename='testvid.flv', content_type='video/x-flv')
        elif type_name == 'event_item':
            form['start_date'] = '10/10/2000'

class ContentTypeConformanceTestCase(ZopeTestCase.TestCase):
    """
    Make sure all the Naaya content types meet certain correctness requirements
    """

    def test_NyContentData_getattr(self):
        """
        The __getattr__ method defined by NyContentData must be the
        __getattr__ method of all Naaya content type classes. It will do the
        right thing and invoke the next __getattr__ in the MRO (method
        resolution order).
        """
        for content_type in content_types:
            if content_type['module'] not in SCHEMA_TESTABLES:
                continue
            self.failUnlessEqual(content_type['_class'].__getattr__.im_func,
                NyContentData.__getattr__.im_func,
                '__getattr__ method of "%s" is wrong' % content_type['meta_type'])


class ConformanceFunctionalTestCase(NaayaFunctionalTestCase):
    """
    Test all content types to make sure they all do certain things
    """

    def afterSetUp(self):
        self.portal.manage_install_pluggableitem('Naaya GeoPoint')
        self.portal.manage_install_pluggableitem('Naaya Extended File')
        self.portal.manage_install_pluggableitem('Naaya Media File')
        self.portal.manage_install_pluggableitem('Naaya Contact')
        from Products.Naaya.NyFolder import addNyFolder
        addNyFolder(self.portal, 'xz_folder', contributor='contributor', submitted=1)
        self.portal.switch_language = 1
        self.portal.gl_add_site_language('fr')
        transaction.commit()
        self.browser_do_login('admin', '')

    def beforeTearDown(self):
        self.browser_do_logout()
        self.portal.gl_del_site_languages(['fr'])
        self.portal.switch_language = 0
        self.portal.manage_delObjects(['xz_folder'])
        self.portal.manage_uninstall_pluggableitem('Naaya Contact')
        self.portal.manage_uninstall_pluggableitem('Naaya Media File')
        self.portal.manage_uninstall_pluggableitem('Naaya Extended File')
        self.portal.manage_uninstall_pluggableitem('Naaya GeoPoint')
        transaction.commit()

    def test_new_schema_property(self):
        """
        Check that we can add a new schema property and have
        it editable and visible end-to-end for each content type
        """
        n = 1

        for content_type in content_types:
            if content_type['module'] not in SCHEMA_TESTABLES:
                continue

            type_name = content_type['module']
            schema = self.portal.portal_schemas.getSchemaForMetatype(content_type['meta_type'])
            schema.addWidget('xzzx', sortorder=200, widget_type='String', label='zxxz')
            transaction.commit()

            # add an object
            self.browser.go('http://localhost/portal/xz_folder/%s' % content_type['add_form'])
            form = self.browser.get_form('frmAdd')
            self.failUnless('xzzx:utf8:ustring' in (c.name for c in form.controls),
                'missing "xzzx" control for %s when adding' % type_name)
            self.browser.clicked(form, form.find_control('title:utf8:ustring'))
            form['title:utf8:ustring'] = 'some title %d' % n
            form['xzzx:utf8:ustring'] = 'the XzZx one true value'
            _fill_specific_form_fields(form, type_name)
            self.browser.submit()

            # make sure the value was set
            obj = self.portal.xz_folder['some-title-%d' % n]
            self.failUnlessEqual(getattr(obj, 'xzzx', None), 'the XzZx one true value',
                'bad/missing "xzzx" value for %s' % type_name)

            # edit the object
            self.browser.go('http://localhost/portal/xz_folder/some-title-%d/edit_html' % n)
            form = self.browser.get_form('frmEdit')
            self.failUnless('xzzx:utf8:ustring' in (c.name for c in form.controls),
                'missing "xzzx" control for %s when editing' % type_name)
            self.browser.clicked(form, form.find_control('xzzx:utf8:ustring'))
            self.browser.submit()
            form = self.browser.get_form('frmEdit')
            self.failUnlessEqual(form['xzzx:utf8:ustring'], 'the XzZx one true value',
                'bad "xzzx" value in edit form for %s' % type_name)
            form['xzzx:utf8:ustring'] = 'the XzZx other true value'
            self.browser.clicked(form, form.find_control('xzzx:utf8:ustring'))
            self.browser.submit()

            # make sure the value was changed
            obj = self.portal.xz_folder['some-title-%d' % n]
            self.failUnlessEqual(getattr(obj, 'xzzx', None), 'the XzZx other true value',
                'bad/missing "xzzx" 2nd value for %s' % type_name)

            # clean up
            self.portal.xz_folder.manage_delObjects(['some-title-%d' % n])
            schema = self.portal.portal_schemas.getSchemaForMetatype(content_type['meta_type'])
            schema.manage_delObjects(['xzzx-property'])
            transaction.commit()
            n += 1

    def test_form_remember_data(self):
        """ Make sure forms don't lose their data when they have an error """
        for content_type in content_types:
            if content_type['module'] not in FORM_TESTABLES:
                continue

            type_name = content_type['module']

            # "create object" form
            self.browser.go('http://localhost/portal/xz_folder/%s' % content_type['add_form'])
            # dont' add title, so the form generates an error
            form = self.browser.get_form('frmAdd')
            form['keywords:utf8:ustring'] = 'no save me'
            self.browser.clicked(form, form.find_control('title:utf8:ustring'))
            self.browser.submit()

            html = self.browser.get_html()
            self.failUnless('frmAdd' in html)
            self.failUnless('Value required for "Title"' in html
                or 'The Title field must have a value.' in html)
            form = self.browser.get_form('frmAdd')
            self.failUnlessEqual(form['keywords:utf8:ustring'], 'no save me',
                'The "add" form did not remember our data (%s)' % type_name)

            self.failIf('test-form-title' in self.portal.xz_folder.objectIds(),
                'Object should not have been created! (%s)' % type_name)

            # create the real object so we can try editing it
            form = self.browser.get_form('frmAdd')
            form['title:utf8:ustring'] = 'test form title'
            form['keywords:utf8:ustring'] = ''
            _fill_specific_form_fields(form, type_name)
            self.browser.clicked(form, form.find_control('title:utf8:ustring'))
            self.browser.submit()

            # make sure the object was created
            ob = self.portal.xz_folder['test-form-title']
            self.failUnlessEqual(ob.meta_type, content_type['meta_type'])

            # try to edit the object, expect form errors
            self.browser.go('http://localhost/portal/xz_folder/test-form-title/edit_html')
            form = self.browser.get_form('frmEdit')
            self.failUnlessEqual(form['title:utf8:ustring'], 'test form title')
            form['title:utf8:ustring'] = ''
            form['keywords:utf8:ustring'] = 'no save me'
            self.browser.clicked(form, form.find_control('title:utf8:ustring'))
            self.browser.submit()

            # see if the form contains errors, and the data we just entered.
            self.failUnless('The form contains errors' in html)
            self.failUnless('Value required for "Title"' in html
                or 'The Title field must have a value.' in html)
            form = self.browser.get_form('frmEdit')
            #self.failUnlessEqual(form['keywords:utf8:ustring'], 'no save me',
            #    'The "edit" form did not remember our data (%s)' % type_name)

            self.failUnlessEqual(self.portal.xz_folder['test-form-title'].keywords, '',
                'The object\'s "keywords" value should have been empty (%s)' % type_name)

            # delete the object, so we can create another one with the same ID later on
            self.portal.xz_folder.manage_delObjects(['test-form-title'])
            transaction.commit()

    def test_translate_object(self):
        """ Make sure the translation interface works properly """
        for content_type in content_types:
            type_name = content_type['module']

            if type_name not in TRANSLATE_TESTABLES:
                continue

            # "create object" form
            self.browser.go('http://localhost/portal/xz_folder/%s' % content_type['add_form'])
            form = self.browser.get_form('frmAdd')
            form['title:utf8:ustring'] = 'ze title'
            _fill_specific_form_fields(form, type_name)
            self.browser.clicked(form, form.find_control('title:utf8:ustring'))
            self.browser.submit()

            # make sure the object was created
            ob = self.portal.xz_folder['ze-title']
            self.failUnlessEqual(ob.meta_type, content_type['meta_type'])

            # try to edit the object in another language
            self.browser.go('http://localhost/portal/xz_folder/ze-title/edit_html?lang=fr')
            form = self.browser.get_form('frmEdit')
            self.failUnlessEqual(form['title:utf8:ustring'], '',
                'Unexpected value in form: "%s" (should be "") (%s)'
                    % (form['title:utf8:ustring'], type_name))
            form['title:utf8:ustring'] = 'le title'
            self.browser.clicked(form, form.find_control('title:utf8:ustring'))
            self.browser.submit()
            self.failIf('The form contains errors' in self.browser.get_html())

            obj = self.portal.xz_folder['ze-title']
            self.failUnlessEqual(obj.getLocalProperty('title', 'en'), 'ze title',
                'The object\'s english "title" value is wrong (%s)' % type_name)
            self.failUnlessEqual(obj.getLocalProperty('title', 'fr'), 'le title',
                'The object\'s french "title" value is wrong (%s)' % type_name)

            # do the "switch to language" operation - move content from 'en' to 'fr'
            self.browser.go('http://localhost/portal/xz_folder/ze-title/edit_html')
            form = self.browser.get_form('switch_to_language')
            self.browser.clicked(form, form.find_control('switchToLanguage:method'))
            self.browser.submit()

            obj = self.portal.xz_folder['ze-title']
            self.failUnlessEqual(obj.getLocalProperty('title', 'en'), '',
                'The new english "title" value is wrong (%s)' % type_name)
            self.failUnlessEqual(obj.getLocalProperty('title', 'fr'), 'ze title',
                'The new french "title" value is wrong (%s)' % type_name)

            # delete the object, so we can create another one with the same ID later on
            self.portal.xz_folder.manage_delObjects(['ze-title'])
            transaction.commit()

    def testCatalog(self):
        """ Make sure objects get cataloged properly """
        for content_type in content_types:
            type_name = content_type['module']
            if type_name not in SCHEMA_TESTABLES:
                continue
            rnd_title = 'title' + str(random())[2:8]

            self.browser.go('http://localhost/portal/xz_folder/%s' % content_type['add_form'])
            form = self.browser.get_form('frmAdd')
            self.assertTrue(form is not None, "%s form cannot be rendered" %
                                        content_type['add_form'])
            form['title:utf8:ustring'] = rnd_title
            _fill_specific_form_fields(form, type_name)
            self.browser.clicked(form, form.find_control('title:utf8:ustring'))
            self.browser.submit()

            self.browser.go('http://localhost/portal/search_html?query=' + rnd_title)
            html = self.browser.get_html()

            # we look for a hyperlink to our object
            self.assertTrue('xz_folder/%s' % rnd_title in html,
                            "Title '%s' not found for '%s' in search results" %
                            (rnd_title, content_type['meta_type']))

            self.portal.xz_folder.manage_delObjects([rnd_title])
            transaction.commit()

class ContentTypesEventsTestCase(NaayaFunctionalTestCase):
    """ Test if events are triggered correctly."""

    handlers = []

    def afterSetUp(self):
        from naaya.content.document.document_item import addNyDocument
        addNyDocument(self.portal.info, id="document", title="Document",
                      contributor='contributor', submitted=1)
        from Products.Naaya.NyFolder import addNyFolder
        addNyFolder(self.portal, 'folder', contributor='contributor',
                    submitted=1)
        transaction.commit()

    def beforeTearDown(self):
        """ Remove all handlers """
        gsm = getGlobalSiteManager()
        for handler in self.handlers:
            gsm.unregisterHandler(handler)

    def _register_handler(self, handler):
        self.handlers.append(handler)
        gsm = getGlobalSiteManager()
        gsm.registerHandler(handler)

    def test_create(self):
        """ Creating an object should trigger the `INyContentObjectAddEvent`
        event. """

        self.browser_do_login('admin', '')

        received_content_types = []

        @adapter(INyContentObjectAddEvent)
        def event_handler(event):
            received_content_types.append(event.context.meta_type)

        self._register_handler(event_handler)

        visited_content_types = []
        for content_type in content_types:
            type_name = content_type['module']
            if type_name not in SCHEMA_TESTABLES:
                continue

            visited_content_types.append(content_type['meta_type'])
            rnd_title = 'title' + str(random())[2:8]
            self.browser.go(self.portal.info.absolute_url() + '/%s' %
                            content_type['add_form'])
            form = self.browser.get_form('frmAdd')
            form['title:utf8:ustring'] = rnd_title
            _fill_specific_form_fields(form, type_name)
            self.browser.clicked(form, form.find_control('title:utf8:ustring'))
            self.browser.submit()
            transaction.commit()

        self.assertEqual(set(visited_content_types),
                         set(received_content_types))
    def test_modify(self):
        """ Modifying an object should trigger the `INyContentObjectEditEvent`
        event. """

        self.browser_do_login('admin', '')

        received_content_types = []

        @adapter(INyContentObjectEditEvent)
        def event_handler(event):
            received_content_types.append(event.context.meta_type)

        self._register_handler(event_handler)

        visited_content_types = []

        for content_type in content_types:
            type_name = content_type['module']
            if type_name not in SCHEMA_TESTABLES:
                continue
            #Count visited content types
            visited_content_types.append(content_type['meta_type'])

            rnd_title = 'title' + str(random())[2:8]
            self.browser.go(self.portal.info.absolute_url() + '/%s' %
                            content_type['add_form'])
            form = self.browser.get_form('frmAdd')
            form['title:utf8:ustring'] = rnd_title
            _fill_specific_form_fields(form, type_name)
            self.browser.clicked(form, form.find_control('title:utf8:ustring'))
            self.browser.submit()

            #Go to objects edit page
            self.browser.go(self.portal.info[rnd_title].absolute_url() +
                            '/edit_html')
            form = self.browser.get_form('frmEdit')
            form['title:utf8:ustring'] = "Modified object"
            _fill_specific_form_fields(form, type_name)
            self.browser.clicked(form, form.find_control('title:utf8:ustring'))
            self.browser.submit()


        self.assertEqual(set(visited_content_types),
                         set(received_content_types))

    def test_approve(self):
        """ Create an unapproved object and approve it - this should trigger an
        ``INyContentObjectApproveEvent`` event.

        """

        visited = False

        @adapter(INyContentObjectApproveEvent)
        def event_handler(event):
            self.visited = True
        self._register_handler(event_handler)

        document = self.portal.info['document']
        document.approved = 0
        document.approveThis()
        self.assertTrue(self.visited)

    def test_unapprove(self):
        """ Create an approved object and unapprove it - this should trigger an
        ``INyContentObjectUnapproveEvent`` event.

        """
        self.visited = False

        @adapter(INyContentObjectUnapproveEvent)
        def event_handler(event):
            self.visited = True
        self._register_handler(event_handler)

        document = self.portal.info['document']
        document.approveThis(approved=0)
        self.assertTrue(self.visited)

    def test_move(self):
        """ If an object is moved it should throw an
        `INyContentObjectMovedEvent` event.

        """

        self.visited = False
        @adapter(INyContentObjectMovedEvent)
        def event_handler(event):
            self.visited = True
            self.assertEqual(event.old_site_path, 'info/document')
            self.assertEqual(event.new_site_path, 'folder/document')
        self._register_handler(event_handler)

        #Move `document` from `info` to `folder`
        self.login() #We need this to perform the stuff bellow (Zope2)
        document_data = self.portal.info.manage_cutObjects('document')
        self.portal.folder.manage_pasteObjects(document_data)
        self.logout()

        self.assertTrue(self.visited)

    def test_move_delete(self):
        """ If an object is moved it should throw an
        `INyContentObjectMovedEvent` event. However this event will not be
        triggered when an object has been deleted

        """

        self.visited = False
        @adapter(INyContentObjectMovedEvent)
        def event_handler(event):
            self.visited = True
        self._register_handler(event_handler)

        #Move `document` from `info` to `folder`
        self.login() #We need this to perform the stuff bellow (Zope2)
        self.portal.info.manage_delObjects(['document'])
        self.logout()
        self.assertFalse(self.visited)

    def test_move_create(self):
        """ If an object is moved it should throw an
        `INyContentObjectMovedEvent` event. However this event will not be
        triggered when an object has been `created`

        """
        events = []
        self.browser_do_login('admin', '')

        @adapter(INyContentObjectMovedEvent)
        def event_handler(event):
            events.append(event)
        self._register_handler(event_handler)

        for content_type in content_types:
            type_name = content_type['module']
            if type_name not in SCHEMA_TESTABLES:
                continue

            rnd_title = 'title' + str(random())[2:8]
            self.browser.go(self.portal.info.absolute_url() + '/%s' %
                            content_type['add_form'])
            form = self.browser.get_form('frmAdd')
            form['title:utf8:ustring'] = rnd_title
            _fill_specific_form_fields(form, type_name)
            self.browser.clicked(form, form.find_control('title:utf8:ustring'))
            self.browser.submit()
            transaction.commit()

        self.assertEqual(events, [])
