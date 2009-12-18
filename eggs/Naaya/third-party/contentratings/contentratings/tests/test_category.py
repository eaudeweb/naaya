import unittest
from zope.interface import Interface, Attribute, directlyProvides, implements
from zope.testing.doctestunit import DocFileSuite
from zope.app.testing import ztapi, placelesssetup
from zope.annotation.interfaces import IAnnotations
from zope.annotation.interfaces import IAttributeAnnotatable
from zope.annotation.attribute import AttributeAnnotations
from zope.app.container.sample import SampleContainer

from contentratings.interfaces import IRatingType
from contentratings.interfaces import IRatingStorage

class ITestRatingType(Interface):

    def rate(value, required):
        """Rate an item"""

    rating = Attribute("The rating attribute")

    dummy_attr = Attribute("Dummy Attribute")

    def __setitem__(name, value):
        """Sets a value"""

    def __getitem__(name):
        """Returns the value"""

    def dummy_method():
        """Dummy"""

# Mark our rating interface as a rating type
directlyProvides(ITestRatingType, IRatingType)

class DummyStorage(object):
    """A storage with no pre-defined attributes"""
    implements(ITestRatingType, IRatingStorage)

    rating = None
    dummy_attr = None
    inaccessible_attribute = True

    def rate(self, value, required):
        return "Rating: %s"%value

    def __setitem__(self, name, value):
        print "item set"

    def __getitem__(self, name):
        return "Dummy item"

    def dummy_method(self):
        return "Dummy Method"

class DummyManager(object):
    """A class that does nothing except get returned by the category factory"""

    def __init__(self, category, context):
        self.category = category
        self.context = context

def setUpCategory(test):
    placelesssetup.setUp(test)
    ztapi.provideAdapter(IAttributeAnnotatable, IAnnotations,
                         AttributeAnnotations)
    container = SampleContainer()
    test.globs = {'my_container': container}
    directlyProvides(container, IAttributeAnnotatable)

def test_suite():
    return unittest.TestSuite((
        DocFileSuite('category_factory.txt',
                     package='contentratings.tests',
                     setUp=setUpCategory,
                     tearDown=placelesssetup.tearDown,
                     ),
        DocFileSuite('rating_manager.txt',
                     package='contentratings.tests',
                     setUp=setUpCategory,
                     tearDown=placelesssetup.tearDown,
                     ),
        DocFileSuite('migration.txt',
                     package='contentratings.tests',
                     setUp=placelesssetup.setUp,
                     tearDown=placelesssetup.tearDown,
                     ),
        ))

if __name__ == '__main__':
   unittest.main(defaultTest='test_suite')
