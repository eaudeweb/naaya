import unittest
from zope.interface import Interface, directlyProvides, classImplements
from zope.testing.doctestunit import DocFileSuite
from zope.app.testing import ztapi, placelesssetup
from zope.annotation.interfaces import IAnnotations
from zope.annotation.interfaces import IAttributeAnnotatable
from zope.annotation.attribute import AttributeAnnotations
from zope.app.container.sample import SampleContainer
from zope.configuration import xmlconfig

import contentratings
from contentratings.bbb import EditorialRating
from contentratings.bbb import UserRating
from contentratings.interfaces import IEditorRatable
from contentratings.interfaces import IUserRatable
from contentratings.interfaces import IEditorialRating
from contentratings.interfaces import IUserRating
from contentratings.interfaces import IRatingType
from contentratings.interfaces import IRatingCategory
from contentratings.interfaces import IRatingManager
from contentratings.interfaces import IRatingStorage
from contentratings.category import RatingCategoryAdapter
from contentratings.rating import Rating, NPRating
from contentratings.storage import UserRatingStorage
from contentratings.storage import EditorialRatingStorage

def baseIntegration(test):
    placelesssetup.setUp(test)
    directlyProvides(IEditorialRating, IRatingType)
    directlyProvides(IUserRating, IRatingType)
    # We use SampleContainers in our tests, so let's make it annotatable
    classImplements(SampleContainer, IAttributeAnnotatable)
    ztapi.provideAdapter(IAttributeAnnotatable, IAnnotations,
                         AttributeAnnotations)
    ztapi.provideAdapter((IRatingCategory, Interface),
                         IRatingManager, RatingCategoryAdapter)
    container = SampleContainer()
    test.globs = {'my_container': container}

def setUpBBB(test):
    baseIntegration(test)
    ztapi.provideAdapter(IEditorRatable, IEditorialRating, EditorialRating)
    ztapi.provideAdapter(IUserRatable, IUserRating, UserRating)
    container = test.globs['my_container']
    directlyProvides(container,
                     IAttributeAnnotatable, IEditorRatable, IUserRatable)


def test_suite():
    return unittest.TestSuite((
        DocFileSuite('README.txt',
                     package='contentratings',
                     setUp=setUpBBB,
                     tearDown=placelesssetup.tearDown),
        DocFileSuite('userstorage.txt',
                     package='contentratings.tests',
                     setUp=placelesssetup.setUp,
                     tearDown=placelesssetup.tearDown,
                     globs = {'storage': UserRatingStorage}),
        DocFileSuite('editorialstorage.txt',
                     package='contentratings.tests',
                     setUp=placelesssetup.setUp,
                     tearDown=placelesssetup.tearDown,
                     globs = {'storage': EditorialRatingStorage}),
        DocFileSuite('rating.txt',
                     package='contentratings.tests',
                     setUp=placelesssetup.setUp,
                     tearDown=placelesssetup.tearDown,
                     globs = {'rating_factory': Rating}),
        DocFileSuite('rating.txt',
                     package='contentratings.tests',
                     setUp=placelesssetup.setUp,
                     tearDown=placelesssetup.tearDown,
                     globs = {'rating_factory': NPRating}),
        DocFileSuite('BBB.txt',
                     package='contentratings.tests',
                     setUp=setUpBBB,
                     tearDown=placelesssetup.tearDown,
                     globs = {'storage': EditorialRatingStorage}),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
