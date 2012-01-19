from naaya.content.contact import contact_item
from subscribers import get_category_location
from Products.Naaya.NyFolder import NyFolder


def patch_addNyContact():
    original = contact_item.addNyContact
    def patched(self, id='', REQUEST=None, contributor=None, **kwargs):
        """
        addNyContact should place the contact in a location based on
        geo_type (Category)

        """
        site = self.getSite()
        # kwargs need to be merged with *args, regardless of applying patch act.
        if contributor is not None:
            kwargs['contributor'] = contributor
        if id is not None:
            kwargs['id'] = id
        if REQUEST is not None:
            schema_raw_data = dict(REQUEST.form)
            kwargs['REQUEST'] = REQUEST
        else:
            schema_raw_data = kwargs

        if (not getattr(site, 'destinet.publisher', False)
            or self != site['who-who']):
            return original(self, **kwargs)

        geo_type = schema_raw_data.get('geo_type', None)
        new_parent = get_category_location(site, geo_type)
        if not new_parent:
            new_parent = self
        return original(new_parent, **kwargs)

    contact_item.addNyContact = patched
    NyFolder.addNyContact = patched
