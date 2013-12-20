"""
Group here other tests related to code in :mod:`naaya.core.zope2util`
"""
from Products.Naaya.tests.NaayaTestCase import NaayaTestCase
from Products.Naaya.NySite import manage_addNySite

class PathsTest(NaayaTestCase):

    def setUp(self):
        super(NaayaTestCase, self).setUp()
        manage_addNySite(self.portal.info,
                         id='subsite', title='subsite', lang='en')

    def test_path_in_site(self):
        from naaya.core.zope2util import path_in_site
        self.assertEqual(path_in_site(self.portal), '')
        self.assertEqual(path_in_site(self.portal.info), 'info')
        self.assertEqual(path_in_site(self.portal.info.subsite), '')

    def test_relative_object_path(self):
        from naaya.core.zope2util import relative_object_path
        subportal = self.portal.info.subsite
        self.assertEqual(relative_object_path(subportal, subportal), '')
        self.assertEqual(relative_object_path(subportal, self.portal), 'info/subsite')
        self.assertEqual(relative_object_path(subportal.info, subportal), 'info')
        self.assertEqual(relative_object_path(subportal.info, self.portal),
                         'info/subsite/info')
        self.assertRaises(ValueError, relative_object_path,
                          self.portal, subportal)

class TestThreadJob(NaayaTestCase):

    def test_thread(self):
        from time import sleep
        from threading import Semaphore
        from naaya.core.zope2util import ofs_path, launch_job
        import transaction

        job_done = Semaphore(0)

        def threaded_job(context):
            context.hello = "world"
            transaction.commit()
            job_done.release()

        folder = self.portal['info']
        launch_job(threaded_job, folder, ofs_path(folder))
        transaction.commit()

        for c in range(100):
            if job_done.acquire(blocking=False):
                break
            sleep(0.1)
        else:
            self.fail("Waited 10 seconds and the job did not finish yet")

        transaction.abort()
        self.assertEqual(folder.hello, "world")