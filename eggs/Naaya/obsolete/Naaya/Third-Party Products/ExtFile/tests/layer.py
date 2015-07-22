#
# Load ZCML to get events configured
#

try:
    from zope.testing import testrunner
    from zope.testing import cleanup
    from Products.Five import zcml
except ImportError:
    USELAYER = 0
else:
    USELAYER = 1

    class ZCML:

        def setUp(cls):
            cleanup.cleanUp()
            zcml._initialized = 0
            zcml.load_site()
        setUp = classmethod(setUp)

        def tearDown(cls):
            cleanup.cleanUp()
            zcml._initialized = 0
        tearDown = classmethod(tearDown)

    class CopySupport(ZCML):

        def setUp(cls):
            # Mark base class as five:deprecatedManageAddDelete
            try:
                from Products.Five.eventconfigure import setDeprecatedManageAddDelete
            except ImportError:
                pass
            else:
                from Products.ExtFile.tests import testCopySupport
                setDeprecatedManageAddDelete(testCopySupport.HookCounter)
        setUp = classmethod(setUp)

        def tearDown(cls):
            pass
        tearDown = classmethod(tearDown)

    # Derive from ZopeLite layer if available
    try:
        from Testing.ZopeTestCase.layer import ZopeLite
    except ImportError:
        pass
    else:
        ZCML.__bases__ = (ZopeLite,)

