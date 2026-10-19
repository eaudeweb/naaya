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

class FolderManageMainPlusTest(NaayaTestCase):

    def test_child_with_modification_time_attribute(self):
        from DateTime import DateTime
        from OFS.Folder import Folder
        from OFS.SimpleItem import SimpleItem
        from naaya.core.zope2util import folder_manage_main_plus

        class PlusFolder(Folder):
            manage_main = folder_manage_main_plus

        class Answer(SimpleItem):
            meta_type = 'Test Answer'

            def __init__(self, id):
                self.id = id
                # as in NaayaSurvey SurveyAnswer
                self.modification_time = DateTime()

        self.portal._setObject('plus', PlusFolder('plus'))
        plus = self.portal.plus
        plus._setObject('answer', Answer('answer'))
        request = self.portal.REQUEST
        for name in ('URL', 'URL1', 'URL2', 'BASEPATH1'):
            request.set(name, plus.absolute_url())
        html = plus.manage_main(plus, request)
        self.assertIn('answer', html)


class JsonDumpsTest(NaayaTestCase):

    def test_script_safe(self):
        import json
        from naaya.core.zope2util import json_dumps
        text = json_dumps({'address': '";</script><b>&', 'country': None})
        for char in '<>&':
            self.assertNotIn(char, text)
        self.assertEqual(json.loads(text),
                         {'address': '";</script><b>&', 'country': None})
