import unittest
from zope.testing import doctestunit
from zope.interface import Interface, directlyProvides
from zope.app.container.sample import SampleContainer
from zope.schema.interfaces import IVocabularyFactory
from zope.app.testing import ztapi
from zope.component.testing import setUp, tearDown
from zope.annotation.interfaces import IAnnotations
from zope.annotation.interfaces import IAttributeAnnotatable
from zope.annotation.attribute import AttributeAnnotations
from contentratings.interfaces import IRatingCategory
from contentratings.interfaces import IRatingManager
from contentratings.category import RatingCategoryAdapter

class DummyView(object):

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        if self.context.can_read:
            return "%s on: %s (%s)"%(self.__class__.__name__,
                                     self.context.title, self.context.name)
        else:
            return '  \n\n' # a blank entry, should be ignored

def setUpViewTests(test):
    setUp(test)
    # Setup our adapter from category to rating api
    ztapi.provideAdapter((IRatingCategory, Interface),
                             IRatingManager, RatingCategoryAdapter)
    ztapi.provideAdapter(IAttributeAnnotatable, IAnnotations,
                         AttributeAnnotations)
    container = SampleContainer()
    directlyProvides(container, IAttributeAnnotatable)
    test.globs = {'my_container': container}


def test_suite():
    return unittest.TestSuite((
        doctestunit.DocFileSuite('aggregator.txt',
                                 package='contentratings.browser',
                                 setUp=setUpViewTests,
                                 tearDown=tearDown,
                                 ),
        doctestunit.DocTestSuite('contentratings.browser.traverser',
                                 setUp=setUpViewTests,
                                 tearDown=tearDown,),
        doctestunit.DocTestSuite('contentratings.browser.utils',
                                 setUp=setUp,
                                 tearDown=tearDown,),
        doctestunit.DocFileSuite('views.txt',
                                 package='contentratings.browser',
                                 setUp=setUpViewTests,
                                 tearDown=tearDown,),
        ))

if __name__ == '__main__':
   unittest.main(defaultTest='test_suite')
