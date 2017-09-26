from Products.naayaUpdater.updates import UpdateScript


class AssignKeywordForUserRole(UpdateScript):
    """ Migration: fix keyword for users with role in EEN
    """
    title = 'Destinet: fix keywords for roles'
    creation_date = 'Ian 10, 2013'
    authors = ['Tiberiu Ichim']
    description = ("Fix the keywords for users after it was lost")

    def _update(self, portal):
        context = portal.restrictedTraverse('who-who/destinet-users')
        auth_tool = portal.getAuthenticationTool()

        for obj in context.objectValues("Naaya Contact"):
            user_id = obj.contributor
            user = auth_tool.getUser(user_id)

            if not user:
                self.log.info("Could not find user for userid %s", user_id)
                continue

            keywords = obj.keywords.split(',')
            keywords = [k.strip() for k in keywords if k.strip()]

            if not "Destinet User" in keywords:
                keywords.append('Destinet User')

            roles = user.roles
            if "EEN Member" in roles and "European Ecotourism Network" not in keywords:
                keywords.append("European Ecotourism Network")
                self.log.info("Added EEN keyword for %s", obj.absolute_url())

            obj.set_localpropvalue('keywords', 'en', ", ".join(set(keywords)))
            self.log.info("Fixed keywords for %s", obj.absolute_url())
            context.recatalogNyObject(obj)

        return True

