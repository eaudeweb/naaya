from Products.NaayaCore.EmailTool import EmailTool
from Products.NaayaCore.managers.utils import slugify, uniqueId
from Products.naayaUpdater.updates import UpdateScript
from naaya.content.contact.contact_item import _create_NyContact_object
from naaya.core.zope2util import ofs_path


class RecreateContactForOldUsers(UpdateScript):
    """ Migration: create NaayaContact for old users which don't have one
    """
    title = "Destinet: create contacts for users that didn't create one"
    creation_date = 'Ian 06, 2014'
    authors = ['Tiberiu ichim']
    description = ("Create a Naaya Contact for all users in acl_users "
                   "that don't have a contact in the "
                   "/who-who/destinet-users folder. This is updated code.")

    def _update(self, portal):

        context = portal.restrictedTraverse('who-who/destinet-users')
        cat = portal['portal_catalog']
        acl_users = portal['acl_users']
        users = acl_users.getUsers()
        auth_tool = portal.getAuthenticationTool()
        #manager = self.request.AUTHENTICATED_USER.getUserName()

        # first, cleanup wrongly created users
        wrong = [o for o in context.objectValues()
                 if o._owner[1] == 'tibiadmin']
        self.log.info("Deleting %s wrong contacts" % len(wrong))
        for obj in wrong:
            cat.uncatalog_object(ofs_path(obj))

        context.manage_delObjects([o.id for o in wrong])

        self.log.info("Migration: start migration of contacts for old users")
        EmailTool.divert_mail()

        counter = 0
        for user in users:
            fullname = auth_tool.getUserFullNameByID(user.name)
            contacts = cat.searchResults(path=ofs_path(context),
                                         contributor=user.name)

            if not contacts:
                counter += 1

                id = uniqueId(
                    slugify(user.name or 'contact', removelist=[]),
                    lambda x: context._getOb(x, None) is not None)

                ob = _create_NyContact_object(context, id, user.name)

                ob.approveThis(1, user.name)    # 1, manager
                #ob.submitThis()

                ob.set_localpropvalue('title', 'en', fullname)
                ob.set_localpropvalue('description', 'en', "")
                #ob.release_date = DateTime()
                new_user = user.__of__(acl_users)
                ob.changeOwnership(user=new_user)
                ob.giveEditRights()

                context.recatalogNyObject(ob)
                #crashes with unicodedecodeerror:
                #notify(NyContentObjectAddEvent(ob, user.name, {}))

                #log post date
                auth_tool.changeLastPost(user.name)

                self.log.info("Migration: %s - added contact for user: %s",
                              counter, id)

        EmailTool.divert_mail(False)
        self.log.info("Migration: end migration")

        return True
