from Products.naayaUpdater.updates import UpdateScript
from Products.naayaUpdater.updates.utils import get_standard_template

class LogoutDirectlyInStandardTemplate(UpdateScript):
    title = ('Change standard template to allow direct logout')
    authors = ['Valentin Dumitru']
    creation_date = 'Apr 10, 2014'

    def _update(self, portal):
        old_logout = ('<a tal:condition="python:username != \'Anonymous User\'" '
                    'tal:attributes="href string:${site_url}/login/logout" '
                    'i18n:translate="">Logout</a> <a tal:condition="python:username != '
                    '\'Anonymous User\'" tal:define="user_full_name python:'
                    'here.getAuthenticationTool().name_from_userid(username) '
                    'or username" tal:attributes="href string:${site_url}/'
                    'login_html" tal:content="string:(${user_full_name})" />')
        new_logout = ('<a tal:condition="python:username != \'Anonymous User\'" '
                    'tal:attributes="href string:${site_url}/login/logout" '
                    'i18n:translate="">Logout</a> <a tal:condition="python:username != '
                    '\'Anonymous User\'" tal:define="user_full_name python:'
                    'here.getAuthenticationTool().name_from_userid(username) '
                    'or username" tal:attributes="href string:${site_url}/'
                    'member_search?${username}" '
                    'tal:content="string:(${user_full_name})" />')

        standard_template = get_standard_template(portal)
        tal = standard_template.read()
        if new_logout in tal:
            self.log.debug('Standard_template already updated')
        else:
            changed = False
            if old_logout in tal:
                tal = tal.replace(old_logout, new_logout)
                changed = True
            if changed:
                standard_template.write(tal)
                self.log.debug('Standard_template updated')
            else:
                self.log.error('Old and new code not in standard_template')
                return False

        return True
