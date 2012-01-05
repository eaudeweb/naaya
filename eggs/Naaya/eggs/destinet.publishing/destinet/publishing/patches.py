from Products.NaayaBase.NyContentType import NyContentType
from naaya.content.contact.contact_item import NyContact


def nycontenttype_object_submitted_message():
    original = NyContentType.object_submitted_message
    def patched(self, REQUEST):
        """
        NyContacts shouldn't do RESPONSE redirect, because their location
        can get changed in naaya.content.base.interfaces.INyContentObjectAddEvent
        handler

        """
        if getattr(self.getSite(), 'destinet.publisher', False):
            if isinstance(self, NyContact):
                return None
        return original(self, REQUEST)
    NyContentType.object_submitted_message = patched
