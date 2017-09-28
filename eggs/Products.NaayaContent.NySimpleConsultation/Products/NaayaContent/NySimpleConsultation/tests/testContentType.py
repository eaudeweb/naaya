# The contents of this file are subject to the Mozilla Public
# License Version 1.1 (the "License"); you may not use this file
# except in compliance with the License. You may obtain a copy of
# the License at http://www.mozilla.org/MPL/
#
# Software distributed under the License is distributed on an "AS
# IS" basis, WITHOUT WARRANTY OF ANY KIND, either express or
# implied. See the License for the specific language governing
# rights and limitations under the License.
#
# The Initial Owner of the Original Code is European Environment
# Agency (EEA).  Portions created by Finsiel Romania and Eau de Web are
# Copyright (C) European Environment Agency.  All
# Rights Reserved.
#
# Authors:
#
# Alin Voinea, Eau de Web
# Batranu David, Eau de Web

from unittest import TestSuite, makeSuite
from Products.NaayaContent.NySimpleConsultation.NySimpleConsultation import \
addNySimpleConsultation
from Products.Naaya.NyFolder import addNyFolder
from Products.Naaya.tests import NaayaTestCase
from DateTime import DateTime


class NaayaContentTestCase(NaayaTestCase.NaayaTestCase):
    """ TestCase for NaayaContent object
    """
    def afterSetUp(self):
        self.login()
        self.portal.manage_install_pluggableitem(
            meta_type='Naaya Simple Consultation'
        )

        #add the test folder
        addNyFolder(self.portal, id='test_folder')
        self.test_folder = self.portal._getOb('test_folder')

    def beforeTearDown(self):
        self.portal.manage_delObjects([self.test_folder.getId()])
        self.logout()

    def test_main(self):
        """ Add, Find, Edit and Delete Naaya Simple Consultation """

        #add NyConsultation
        addNySimpleConsultation(self.test_folder,
                                id='sc1',
                                title='sc1',
                                lang='en')

        addNySimpleConsultation(self.test_folder,
                                id='sc1_fr',
                                title='sc1_fr',
                                lang='fr')

        meta = self.test_folder.objectValues(['Naaya Simple Consultation'])

        #get added NyConsultation
        for x in meta:
            if x.getLocalProperty('title', 'en') == 'sc1':
                meta = x
            if x.getLocalProperty('title', 'fr') == 'sc1_fr':
                meta_fr = x

        self.assertEqual(meta.getLocalProperty('title', 'en'), 'sc1')
        self.assertEqual(meta_fr.getLocalProperty('title', 'fr'), 'sc1_fr')

        #change NyConsultation title
        meta.saveProperties(title='sc1_edited', lang='en')
        meta_fr.saveProperties(title='sc1_fr_edited', lang='fr')

        self.assertEqual(meta.getLocalProperty('title', 'en'),
                         'sc1_edited')

        self.assertEqual(meta_fr.getLocalProperty('title', 'fr'),
                         'sc1_fr_edited')

        #delete NyConsultation
        self.test_folder.manage_delObjects([meta.getId(), meta_fr.getId()])

        meta = self.test_folder.objectValues(['Naaya Simple Consultation'])
        self.assertEqual(meta, [])

    def test_metadata(self):
        """ Test Simple Consultation metadata """
        releasedate = DateTime()
        #add Consultation with full fields
        fields = {'id':'scs_meta',
                  'title':'Simple consultation metadata test',
                  'description':'This is a simple consultation object',
                  'sortorder':'100',
                  'start_date':'11/11/1111',
                  'end_date':'12/12/1212',
                  'public_reg':'1',
                  'allow_file':'1',
                  'contributor':'contributor',
                  'releasedate':releasedate,
                  'lang':'en',
                  'REQUEST':None}

        addNySimpleConsultation(self.test_folder,
                                id=fields['id'],
                                title=fields['title'],
                                description=fields['description'],
                                sortorder=fields['sortorder'],
                                start_date=fields['start_date'],
                                end_date=fields['end_date'],
                                public_registration=fields['public_reg'],
                                allow_file=fields['allow_file'],
                                contributor=fields['contributor'],
                                releasedate=fields['releasedate'],
                                lang=fields['lang'],
                                REQUEST=fields['REQUEST'])

        #get consultation object
        cns = self.test_folder._getOb(fields['id'])

        self.failUnlessEqual(fields['id'],
                             cns.__dict__['id'])

        self.failUnlessEqual(fields['title'],
                             cns.getLocalProperty('title',
                                                  fields['lang'])
                             )

        self.failUnlessEqual(fields['description'],
                             cns.getLocalProperty('description',
                                                  fields['lang'])
                             )

        self.failUnlessEqual(int(fields['sortorder']),
                             cns.__dict__['sortorder'])

        self.failUnlessEqual(DateTime(fields['start_date']),
                             cns.__dict__['start_date'])

        self.failUnlessEqual(DateTime(fields['end_date']),
                             cns.__dict__['end_date'])

        self.failUnlessEqual(fields['public_reg'],
                             cns.__dict__['public_registration'])

        self.failUnlessEqual(fields['allow_file'],
                             cns.__dict__['allow_file'])

        self.failUnlessEqual(fields['contributor'],
                             cns.__dict__['contributor'])

        self.failUnlessAlmostEqual(fields['releasedate'],
                             cns.__dict__['releasedate'])

        #modify metadata
        fields['title'] = 'modified title'
        fields['description'] = 'modified description'
        fields['sortorder'] = '101'
        fields['start_date'] = '01/01/1001'
        fields['end_date'] = '02/02/2002'
        fields['public_reg'] = ''
        fields['allow_file'] = ''

        cns.saveProperties(
            title=fields['title'],
            description=fields['description'],
            sortorder=fields['sortorder'],
            start_date=fields['start_date'],
            end_date=fields['end_date'],
            public_registration=fields['public_reg'],
            allow_file=fields['allow_file'],
            lang=fields['lang'],
        )


        self.failUnlessEqual(fields['id'],
                             cns.__dict__['id'])

        self.failUnlessEqual(fields['title'],
                             cns.getLocalProperty('title',
                                                  fields['lang'])
                             )

        self.failUnlessEqual(fields['description'],
                             cns.getLocalProperty('description',
                                                  fields['lang'])
                             )

        self.failUnlessEqual(int(fields['sortorder']),
                             cns.__dict__['sortorder'])

        self.failUnlessEqual(DateTime(fields['start_date']),
                             cns.__dict__['start_date'])

        self.failUnlessEqual(DateTime(fields['end_date']),
                             cns.__dict__['end_date'])

        self.failUnlessEqual(fields['public_reg'],
                             cns.__dict__['public_registration'])

        self.failUnlessEqual(fields['allow_file'],
                             cns.__dict__['allow_file'])

        self.failUnlessEqual(fields['contributor'],
                             cns.__dict__['contributor'])

        self.failUnlessAlmostEqual(fields['releasedate'],
                             cns.__dict__['releasedate'])

    def test_main_exfile(self):
        """ Test the simple consultation exfile functionality """
        addNySimpleConsultation(self.test_folder, id='scs')
        scs = self.test_folder._getOb('scs')

        #no exfile should exist
        exfile = scs.get_exfile
        self.failUnlessEqual(exfile(), None)

        #add exfile
        from os import path
        from StringIO import StringIO
        f=open(path.join(path.dirname(__file__), 'test.txt'), 'rb')
        exf = StringIO(f.read())
        f.close()
        exf.filename = 'test.txt'
        self.failUnlessRaises(ValueError, scs.saveProperties, file=exfile)
        scs.saveProperties(title='scs', file=exf, lang='en')

        #test exfile presence
        self.failUnlessEqual(bool(exfile()), True)


def test_suite():
    suite = TestSuite()
    suite.addTest(makeSuite(NaayaContentTestCase))
    return suite
