# from naaya.content.base.events import NyContentObjectAddEvent
# from zope.event import notify
from Products.Five import BrowserView
from Products.NaayaCore.EmailTool import EmailTool
from Products.NaayaCore.managers.utils import slugify, uniqueId
from naaya.content.contact.contact_item import _create_NyContact_object
import logging
import transaction

logger = logging.getLogger("destinet.extra")


class MigrationCreateContactForOldUsers(BrowserView):
    """ Migration: create NaayaContact for old users which don't have one
    """

    def __call__(self):
        cat = self.context.portal_catalog
        users = self.context.acl_users.getUsers()
        auth_tool = self.context.getAuthenticationTool()
        context = self.context.restrictedTraverse('who-who/destinet-users')
        #approved, approved_by = 1, self.request.AUTHENTICATED_USER.getUserName()
        approved, approved_by = 0, None

        logger.info("Migration: start migration")
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

                transaction.commit()
                logger.info("Migration: %s - added contact for user: %s", counter, id)

        EmailTool.divert_mail(False)
        logger.info("Migration: end migration")
        return "Migrated %s contacts" % counter


class MigrationSetKeywordsForDestinetUsers(BrowserView):
    """ Migration: create NaayaContact for old users which don't have one
    """

    def __call__(self):
        context = self.context.restrictedTraverse('who-who/destinet-users')
        langs = self.context.gl_get_languages()

        for obj in context.objectValues("Naaya Contact"):
            for lang in langs:
                v = obj.getLocalAttribute("keywords", lang)
                if not "Destinet User" in v:
                    if v.strip():
                        v += ", Destinet User"
                    else:
                        v = "Destinet User"
                obj.set_localpropvalue('keywords', lang, 'Destinet user')
                context.recatalogNyObject(obj)

        return "done"
