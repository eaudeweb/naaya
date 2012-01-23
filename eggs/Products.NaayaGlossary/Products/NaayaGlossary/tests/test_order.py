""" Ordering of the Glossary """
import transaction
import urllib
try:
    import simplejson as json
except ImportError:
    import json
from Products.Naaya.tests.NaayaFunctionalTestCase import NaayaFunctionalTestCase
import helpers

class TestOrdering(NaayaFunctionalTestCase):
    def afterSetUp(self):
        self.glossary = helpers.make_glossary(self.portal)
        self.glossary.manage_addGlossaryFolder('1', "Bucket")
        self.glossary._getOb('1').manage_addGlossaryElement('11', "Element")
        self.glossary.manage_addGlossaryFolder('2', "Bucket2")
        self.glossary.manage_addGlossaryFolder('3', "Bucket3")
        transaction.commit()

    def test_get_json_tree(self):
        """ Get the current order in JSON format """
        self.browser.go(self.glossary.absolute_url() +
                '/get_json_tree')
        data = json.loads(self.browser.get_html())
        self.assertEqual(data['attributes']['id'], 'my_glossary')
        self.assertEqual(data['attributes']['rel'], 'root')
        self.assertEqual(data['data']['title'], 'my_glossary')
        self.assertEqual(len(data['children']), 3)
        self.assertEqual(data['children'][0]['attributes']['id'], '1')
        self.assertEqual(data['children'][0]['attributes']['rel'], 'tree')
        self.assertEqual(len(data['children'][0]['children']), 1)
        self.assertEqual(
                data['children'][0]['children'][0]['attributes']['id'], '11')

    def test_save_order(self):
        """ Set bucket2 in front of bucket1 """
        self.browser_do_login('admin', '')
        br = self.browser._browser #mechanize.Browser
        data = urllib.urlencode({
            'data': """{
    "attributes": {
        "id": "my_glossary",
        "rel": "root"
    },
    "data": {
        "state": "open",
        "title": "my_glossary"
    },
    "children": [
        {
            "attributes": {
                "id": "2",
                "rel": "tree"
            },
            "data": {
                "title": "Bucket2",
                "icon": "http://localhost:8081/portal/my_glossary/misc_/NaayaGlossary/folder.gif"
            }
        },
        {
            "attributes": {
                "id": "1",
                "rel": "tree"
            },
            "data": {
                "state": "open",
                "title": "Bucket",
                "icon": "http://localhost:8081/portal/my_glossary/misc_/NaayaGlossary/folder.gif"
            },
            "children": [
                {
                    "attributes": {
                        "id": "11",
                        "rel": "node"
                    },
                    "data": {
                        "title": "Element",
                        "icon": "http://localhost:8081/portal/my_glossary/misc_/NaayaGlossary/element.gif"
                    }
                }
            ]
        },
        {
            "attributes": {
                "id": "3",
                "rel": "tree"
            },
            "data": {
                "title": "Bucket3",
                "icon": "http://localhost:8081/portal/my_glossary/misc_/NaayaGlossary/folder.gif"
            }
        }
    ]
}""",
        })
        response = br.open(self.glossary.absolute_url() + '/save_order', data)
        self.assertEqual(response.get_data(), 'OK')
        self.assertEqual(self.glossary.objectIds()[:3], ['2', '1', '3'])

