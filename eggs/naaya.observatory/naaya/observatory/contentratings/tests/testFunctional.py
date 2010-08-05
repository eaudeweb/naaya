#Python imports
from unittest import TestSuite, makeSuite

#Zope imports
from Testing import ZopeTestCase
from zope.configuration import xmlconfig
from zope.component import getAdapter
import transaction

#Naaya imports
from Products.Naaya.tests.NaayaFunctionalTestCase import NaayaFunctionalTestCase

from Products.NaayaCore.SchemaTool.widgets.geo import Geo
from naaya.content.geopoint.geopoint_item import addNyGeoPoint

from contentratings.interfaces import IUserRating

#naaya.observatory imports
from naaya.observatory.contentratings import initialize
from naaya.observatory.contentratings.views import ObservatoryRatingView
from naaya.observatory.contentratings.views import RatingOutOfBoundsError

# this does not retrieve the context if needed get the context first
initialize(context=None)

class NyRatingsAdaptTestCase(NaayaFunctionalTestCase):
    """ Test the new rating category """

    def afterSetUp(self):
        self.portal.manage_install_pluggableitem('Naaya GeoPoint')
        addNyGeoPoint(self.portal.info, 'mygeopoint', title='My GeoPoint',
                contributor='contributor', geo_location=Geo('-13', '-13'),
                submitted=1)
        transaction.commit()

    def beforeTearDown(self):
        self.portal.info.manage_delObjects(['mygeopoint'])
        self.portal.manage_uninstall_pluggableitem('Naaya GeoPoint')
        transaction.commit()

    def testRatingCategories(self):
        ur = IUserRating(self.portal.info.mygeopoint)
        self.assertEqual(ur.name, u'')
        self.assertEqual(ur.averageRating, 0.0)
        self.assertEqual(ur.numberOfRatings, 0)

        ur.rate(3, 'me')
        ur.rate(4, 'you')
        self.assertEqual(ur.averageRating, 3.5)
        self.assertEqual(ur.numberOfRatings, 2)

        obr = getAdapter(self.portal.info.mygeopoint,
                IUserRating, name=u'Observatory Rating')
        self.assertEqual(obr.name, u'Observatory Rating')
        self.assertEqual(obr.averageRating, 0.0)
        self.assertEqual(obr.numberOfRatings, 0)

        obr.rate(5, 'me')
        self.assertEqual(obr.averageRating, 5.0)
        self.assertEqual(obr.numberOfRatings, 1)

        obr.remove_rating('me')
        self.assertEqual(obr.numberOfRatings, 0)

    def testObservatoryRatingView(self):
        orv = ObservatoryRatingView(self.portal.info.mygeopoint, None)
        self.assertEqual(orv.averageRating, 0.0)

        obr = getAdapter(self.portal.info.mygeopoint,
                IUserRating, name=u'Observatory Rating')
        obr.rate(5, 'me')

        self.assertRaises(RatingOutOfBoundsError, orv, None, None)

        obr.rate(4, 'you')
        self.assertEqual(orv.averageRating, 4.5)
        self.assertEqual(orv.numberOfRatings, 2)

        self.assertRaises(RatingOutOfBoundsError, orv, None, None)

        obr.rate(3, 'you')
        self.assertEqual(orv.averageRating, 4.0)
        self.assertEqual(orv.numberOfRatings, 2)

def test_suite():
    suite = TestSuite()
    suite.addTest(makeSuite(NyRatingsAdaptTestCase))
    return suite

