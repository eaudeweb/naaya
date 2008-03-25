Naaya updater
=============

1. How to write a custom update
-------------------------------

- Create a custom python script (you can find custom update scripts in the naayaUpdater/doc/templates/ directory):
    - if the update concerns Naaya, place it in the naayaUpdater/updates directory;
    - if not place it in the related product/updates directory (for example Products/NaayaForum/updates/)
      If this directory doesn't exists, copy it from Products/naayaUpdater/doc/updates;

- Subclass naayaUpdater.NaayaContentUpdater.NaayaContentUpdater:

    from Products.naayaUpdater.updates import nyUpdateLogger as logger
    from Products.naayaUpdater.NaayaContentUpdater import NaayaContentUpdater

    class MyCustomUpdateClass(NaayaContentUpdater):
        # Do update

- Override update_meta_type:

    Example:
        self.update_meta_type = ['Naaya Document', 'Naaya URL']
    or:
        self.update_meta_type = 'Naaya Document'

- Implement/override the following methods:
  
    def _verify_doc(self, doc):
        """ 
        @param doc: A Naaya Content Type found using portal_catalog;
        @type doc: Naaya Content Type;
        @returns doc if it needs to be updated or None;
        """
        return doc
    
    def _update(self):
        """ Update all documents returned by _verify_doc """
        updates = self.list_updates()
        for update in updates:
            # Do update
            # log what you updated
            logger.debug('Update document %s', update.absolute_url())
            
- Optionally you can override _list_updates:

    def _list_updates(self):
        """ Return all objects that need update """
        #
        # Get Naaya Sites
        #
        for site in sites:
            #
            # Get Naaya objects to update (Using portal_catalog or not)
            #
            for nyobject in nyobjects:
                nyobject = self._verify_doc(nyobject)
                if nyobject:
                    yield nyobject

- Register update by defining a register method in your module that returns an instance of your class:

    def register(uid):
        return MyCustomUpdateClass(uid)
