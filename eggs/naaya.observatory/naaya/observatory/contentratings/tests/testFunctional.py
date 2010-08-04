#Python imports
from unittest import TestSuite, makeSuite

#Zope imports
from Testing import ZopeTestCase
from zope.configuration import xmlconfig

#Naaya imports
from Products.Naaya.tests.NaayaFunctionalTestCase import NaayaFunctionalTestCase

from Products.NaayaCore.SchemaTool.widgets.geo import Geo
from naaya.content.geopoint.geopoint_item import addNyGeoPoint

#naaya.observatory imports
from naaya.observatory.contentratings import initialize

# this does not retrieve the context if needed get the context first
initialize(context=None)

class NyRatingsAdaptTestCase(NaayaFunctionalTestCase):
    """ Test the new rating category """

    def afterSetUp(self):
        self.portal.manage_install_pluggableitem('Naaya GeoPoint')
        addNyGeoPoint(self.portal.info, 'mygeopoint', title='My GeoPoint',
                contributor='contributor', geo_location=Geo('-13', '-13'),
                submitted=1)
        import transaction; transaction.commit()

    def beforeTearDown(self):
        self.portal.info.manage_delObjects(['mygeopoint'])
        self.portal.manage_uninstall_pluggableitem('Naaya GeoPoint')
        import transaction; transaction.commit()

    def testRatingCategories(self):
        from contentratings.interfaces import IUserRating
        ur = IUserRating(self.portal.info.mygeopoint)
        self.assertEqual(ur.name, u'')
        self.assertEqual(ur.averageRating, 0.0)
        self.assertEqual(ur.numberOfRatings, 0)

        ur.rate(3, 'me')
        ur.rate(4, 'you')
        self.assertEqual(ur.averageRating, 3.5)
        self.assertEqual(ur.numberOfRatings, 2)

        from zope.component import getAdapter
        obr = getAdapter(self.portal.info.mygeopoint,
                IUserRating, name=u'Observatory Rating')
        self.assertEqual(obr.name, u'Observatory Rating')
        self.assertEqual(obr.averageRating, 0.0)
        self.assertEqual(obr.numberOfRatings, 0)

        obr.rate(5, 'me')
        self.assertEqual(obr.averageRating, 5.0)
        self.assertEqual(obr.numberOfRatings, 1)


def test_suite():
    suite = TestSuite()
    suite.addTest(makeSuite(NyRatingsAdaptTestCase))
    return suite

