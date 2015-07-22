#Python imports

#Zope imports
from AccessControl import ClassSecurityInfo
from AccessControl.Permission import Permission

#Naaya imports
from Products.naayaUpdater.updates import UpdateScript

class AuthenticatedSkipCaptcha(UpdateScript):
    """ Set authenticated users to have the skip captcha permission """
    title = 'Give "Skip Captcha" to authenticated users'
    creation_date = 'May 23, 2013'
    authors = ['Valentin Dumitru']
    security = ClassSecurityInfo()

    security.declarePrivate('_update')
    def _update(self, portal):
        skip_captcha_perm = Permission('Naaya - Skip Captcha', (), portal)
        roles_with_skip_captcha = skip_captcha_perm.getRoles()
        if 'Authenticated' not in roles_with_skip_captcha:
            roles_with_skip_captcha.append('Authenticated')
            skip_captcha_perm.setRoles(roles_with_skip_captcha)
            self.log.debug('Skip Captcha permission assigned to Authenticated')
        else:
            self.log.debug('Authenticated already has the permission')
        return True
