#Python imports

#Zope imports
from AccessControl import ClassSecurityInfo

#Naaya imports
from Products.naayaUpdater.updates import UpdateScript 
from naaya.core.utils import force_to_unicode

class DisplayComments(UpdateScript):
    """ Script for displaying content """
    title = 'Display all comments in site'
    creation_date = 'Mar 27, 2012'
    authors = ['Valentin Dumitru']
    description = 'Display all comments in site'
    security = ClassSecurityInfo()

    security.declarePrivate('_update')
    def _update(self, portal):
        catalog = portal.portal_catalog
        auth_tool = portal.getAuthenticationTool()
        comments = [brain.getObject() for brain in catalog.search({'meta_type': 'Naaya Comment'})]
        for comment in comments:
            user_id = comment.author.encode('ascii')
            try:
                user_ob = auth_tool.get_user_info(user_id)
                user_name = getattr(user_ob, 'full_name', None)
                if not user_name:
                    user_name = getattr(user_ob, 'firstname', '') + getattr(user_ob, 'lastname', '')
            except KeyError:
                user_name = 'User not found: "%s"' % user_id
            self.log.info('%r (%s) added %s' %
                (user_name, comment.author,
                    comment.absolute_url()))
        return True

class DisplayPermissionAddComments(UpdateScript):
    """ Script for displaying content """
    title = 'Display objects with unsecure permission to comment'
    creation_date = 'Mar 27, 2012'
    authors = ['Valentin Dumitru']
    description = ('Display all objects where Anonymous or Authenticated have '
                    'permission to comment')
    security = ClassSecurityInfo()

    security.declarePrivate('_update')
    def _update(self, portal):
        catalog = portal.portal_catalog
        objects = []
        for brain in catalog.search({}):
            try:
                objects.append(brain.getObject())
            except:
                continue
        found = False
        unsafe_roles = ['Anonymous', 'Authenticated']
        for role in portal.rolesOfPermission('Naaya - Add comments for content'):
            for unsafe_role in unsafe_roles:
                if unsafe_role == role['name'] and role['selected']:
                    found = True
                    self.log.info('%s: %s' % (unsafe_role, portal.absolute_url()+'/manage_access'))
        for object in objects:
            try:
                for role in object.rolesOfPermission('Naaya - Add comments for content'):
                    for unsafe_role in unsafe_roles:
                        if unsafe_role == role['name'] and role['selected']:
                            found = True
                            self.log.info('%s: %s' % (unsafe_role, object.absolute_url()+'/manage_access'))
            except:
                pass
        if not found:
            self.log.info('No objects affected')
        return True

class DisplayOpenForComments(UpdateScript):
    """ Script for displaying content """
    title = 'Display all objects open for comments in site'
    creation_date = 'Mar 27, 2012'
    authors = ['Valentin Dumitru']
    description = 'Display all objects open for comments in site'
    security = ClassSecurityInfo()

    security.declarePrivate('_update')
    def _update(self, portal):
        catalog = portal.portal_catalog
        objects = []
        for brain in catalog.search({}):
            try:
                objects.append(brain.getObject())
            except:
                continue
        for object in objects:
            if getattr(object, 'discussion', None):
                self.log.info(object.absolute_url())
        return True

class DisplayForumMessages(UpdateScript):
    """ Script for displaying content """
    title = 'Display all Naaya Forum Messages in site'
    creation_date = 'Mar 27, 2012'
    authors = ['Valentin Dumitru']
    description = 'Display all Naaya Forum Messages in site'
    security = ClassSecurityInfo()

    security.declarePrivate('_update')
    def _update(self, portal):
        catalog = portal.portal_catalog
        auth_tool = portal.getAuthenticationTool()
        objects = [brain.getObject() for brain in catalog.search({'meta_type': 'Naaya Forum Message'})]
        for object in objects:
            user_id = object.author.encode('ascii')
            try:
                user_ob = auth_tool.get_user_info(user_id)
                user_name = getattr(user_ob, 'full_name', None)
                if not user_name:
                    user_name = getattr(user_ob, 'firstname', '') + getattr(user_ob, 'lastname', '')
            except KeyError:
                user_name = 'User not found: "%s"' % user_id
            self.log.info('%r (%s) added %s' %
                (user_name, object.author,
                    object.absolute_url()))
        return True
