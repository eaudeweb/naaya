from Products.naayaUpdater.updates import UpdateScript
from Products.NaayaCore.EmailTool import EmailTool
from Products.NaayaCore.managers.utils import slugify, uniqueId
from naaya.content.contact.contact_item import _create_NyContact_object


class CreateContactForOldUsers(UpdateScript):
    """ Migration: create NaayaContact for old users which don't have one
    """
    title = "Destinet: create contacts for users that didn't create one"
    creation_date = 'Dec 17, 2013'
    authors = ['Tiberiu ichim']
    description = ("Create a Naaya Contact for all users in acl_users that "
                   "don't have a contact in the /who-who/destinet-users folder")

    def _update(self, portal):
        cat = portal['portal_catalog']
        users = portal['acl_users'].getUsers()
        auth_tool = portal.getAuthenticationTool()
        context = portal.restrictedTraverse('who-who/destinet-users')
        #approved, approved_by = 1, self.request.AUTHENTICATED_USER.getUserName()
        approved, approved_by = 0, None

        self.log.info("Migration: start migration of contacts for old users")
        EmailTool.divert_mail()

        counter = 0
        for user in users:
            fullname = auth_tool.getUserFullNameByID(user.name)
            contacts = cat.searchResults(meta_type='Naaya Contact', title=fullname)

            if not contacts:
                counter += 1

                id = uniqueId(slugify(user.name or 'contact', removelist=[]),
                    lambda x: context._getOb(x, None) is not None)

                ob = _create_NyContact_object(context, id, user.name)

                ob.approveThis(approved, approved_by)
                ob.submitThis()

                ob.title = auth_tool.getUserFullNameByID(id)
                ob.description = ''

                context.recatalogNyObject(ob)
                #crashes with unicodedecodeerror:
                #notify(NyContentObjectAddEvent(ob, user.name, {}))

                #log post date
                auth_tool.changeLastPost(user.name)

                self.log.info("Migration: %s - added contact for user: %s", counter, id)

        EmailTool.divert_mail(False)
        self.log.info("Migration: end migration")

        return True
