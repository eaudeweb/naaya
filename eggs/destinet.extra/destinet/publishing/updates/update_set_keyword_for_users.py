from Products.naayaUpdater.updates import UpdateScript


class SetKeywordsForDestinetUsers(UpdateScript):
    """ Migration: create NaayaContact for old users which don't have one
    """
    title = 'Destinet: set the Destinet user keyword for all Naaya Contacts'
    creation_date = 'Dec 17, 2013'
    authors = ['Tiberiu Ichim']
    description = ("Add the 'Destinet user' keyword to all contacts in "
                   "destinet-user folder")

    def _update(self, portal):
        context = portal.restrictedTraverse('who-who/destinet-users')
        langs = portal.gl_get_languages()

        for obj in context.objectValues("Naaya Contact"):
            for lang in langs:
                v = obj.getLocalAttribute("keywords", lang)
                if not "Destinet User" in v:
                    if v.strip():
                        v += ", Destinet User"
                    else:
                        v = "Destinet User"

                obj.set_localpropvalue('keywords', lang, v)
            self.log.info("Set the destinet user keyword for %s",
                              obj.absolute_url())
            context.recatalogNyObject(obj)

        return True
