from naaya.content.base.tests.common import _CommonContentTest
from naaya.content.contact.contact_item import addNyContact

class ContactCommonTest(_CommonContentTest):

    def add_object(self, parent):
        ob = parent[addNyContact(parent, title='My contact')]
        ob.approveThis()
        return ob
