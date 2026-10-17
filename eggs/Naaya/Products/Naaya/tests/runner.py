"""naaya-testrunner: start Zope from $NAAYA_ZOPE_CONF, then run zope.testrunner."""
import os
import sys


def main():
    zope_conf = os.environ.get('NAAYA_ZOPE_CONF')
    if not zope_conf:
        sys.exit("Set NAAYA_ZOPE_CONF to the zope.conf of the instance")
    # Zope must run before the test modules are imported: they need its ZCML and environment
    from Products.Naaya.tests.zope_environment import zope_test_environment
    tzope = zope_test_environment(zope_conf)
    from Products.Naaya.tests.NaayaTestCase import NaayaTestLayer
    NaayaTestLayer._tzope = tzope
    from zope.testrunner import run
    run()
