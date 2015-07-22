from naaya.content.base.tests.common import _IconTests
from naaya.content.contact.contact_item import addNyContact

class ContactIconTests(_IconTests):

    def add_object(self, parent):
        parent.getSite().manage_install_pluggableitem('Naaya Contact')
        ob = parent[addNyContact(parent, title='My contact')]
        ob.approveThis()
        return ob
