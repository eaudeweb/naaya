from os import path
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Products.naayaUpdater.updates import UpdateScript
from Products.naayaUpdater.updates.utils import get_standard_template
from naaya.groupware import groupware_site
from Products.NaayaCore.LayoutTool.DiskFile import manage_addDiskFile
from Products.NaayaCore.LayoutTool.DiskTemplate import manage_addDiskTemplate


class LogoutDirectlyInStandardTemplate(UpdateScript):
    title = ('Change standard template to allow direct logout')
    authors = ['Valentin Dumitru']
    creation_date = 'Apr 10, 2014'

    def _update(self, portal):
        old_logout = [
            ('<a tal:condition="python:username != \'Anonymous User\'" '
             'tal:attributes="href string:${site_url}/login_html" '
             'i18n:translate="">Logout <tal:block tal:content="string:'
             '(${username})" i18n:name="username" /></a>'),
            ('<a tal:condition="python:username != \'Anonymous User\'" '
             'tal:attributes="href string:${site_url}/login_html" '
             'i18n:translate="">Logout <tal:block tal:content="string:'
             '(${username})" i18n:name="username"/></a>'),
            ('<a tal:condition="python:username != \'Anonymous User\'" '
             'tal:attributes="href string:${site_url}/login/logout" '
             'i18n:translate="">Logout</a> <a tal:condition="python:'
             'username != \'Anonymous User\'" tal:define="'
             'user_full_name python:here.getAuthenticationTool().'
             'name_from_userid(username) or username" tal:attributes="'
             'href string:${site_url}/login_html" tal:content="string:'
             '(${user_full_name})" />'),
            ('<a tal:condition="python:username != \'Anonymous User\'" '
             'tal:attributes="href string:${site_url}/login/logout" '
             'i18n:translate="">Logout</a> <a tal:condition="'
             'python:username != \'Anonymous User\'" tal:define="'
             'user_full_name python:here.getAuthenticationTool().'
             'name_from_userid(username) or username" tal:attributes="'
             'href string:${site_url}/member_search?${username}" '
             'tal:content="string:(${user_full_name})" />')
        ]
        new_logout = (
            '<a tal:condition="python:username != \'Anonymous User\'" '
            'tal:attributes="href string:${site_url}/login/logout" '
            'i18n:translate="">Logout</a> <a tal:condition="python:username !='
            ' \'Anonymous User\'" tal:define="user_full_name python:'
            'here.getAuthenticationTool().name_from_userid(username) '
            'or username" tal:attributes="href string:${site_url}/'
            'member_search?search_string=${username}" '
            'tal:content="string:(${user_full_name})" />')

        standard_template = get_standard_template(portal)
        tal = standard_template.read()
        if new_logout in tal:
            self.log.debug('Standard_template already updated')
        else:
            changed = False
            for tal_code in old_logout:
                if tal_code in tal:
                    tal = tal.replace(tal_code, new_logout)
                    changed = True
            if changed:
                standard_template.write(tal)
                self.log.debug('Standard_template updated')
            else:
                self.log.error('Old and new code not in standard_template')
                return False

        return True


class SignupName(UpdateScript):
    title = ('Change standard template to to display Signup name on top bar')
    authors = ['Valentin Dumitru']
    creation_date = 'Nov 07, 2019'

    def _update(self, portal):
        old_logout = [
            ('<li><a tal:condition="python:username != \'Anonymous User\'" '
             'tal:attributes="href string:${site_url}/login/logout" '
             'i18n:translate="">Logout</a> <a tal:condition="python:username '
             '!= \'Anonymous User\'" tal:define="user_full_name '
             'python:here.getAuthenticationTool().name_from_userid(username) '
             'or username" tal:attributes="href string:${site_url}/'
             'member_search?search_string=${username}" tal:content="string:'
             '(${user_full_name})" /></li>'),
            ('<li><a tal:condition="python:username != \'Anonymous User\'" '
             'tal:attributes="href string:${site_url}/login/logout" '
             'i18n:translate="">Logout</a> <a id="username" tal:condition="'
             'python:username != \'Anonymous User\'" tal:define="user_full_'
             'name python:here.getAuthenticationTool().name_from_userid('
             'username) or username" tal:attributes="href string:${site_url}/'
             'member_search?search_string=${username}" tal:content="string:'
             '(${user_full_name})" /></li>'),
            ('<li><a tal:condition="python:username != \'Anonymous User\'" '
             'tal:attributes="href string:${site_url}/login/logout" '
             'i18n:translate="">Logout</a> <a tal:condition="python:username '
             '!= \'Anonymous User\'" tal:define="user_full_name python:here.'
             'getAuthenticationTool().name_from_userid(username) or username" '
             'tal:attributes="href string:${site_url}/login_html" tal:content='
             '"string:(${user_full_name})" /></li>'),
        ]
        new_logout = (
            '<li tal:define="signup_name here/get_user_name|nothing">'
            '<a tal:condition="python:username != \'Anonymous User\'" '
            'tal:attributes="href string:${site_url}/login/logout" '
            'i18n:translate="">Logout</a> <a tal:condition="python:username '
            '!= \'Anonymous User\' and not signup_name" tal:define="'
            'user_full_name python:here.getAuthenticationTool().'
            'name_from_userid(username) or username" tal:attributes="href '
            'string:${site_url}/member_search?search_string=${username}" '
            'tal:content="string:(${user_full_name})" /> <span tal:condition="'
            'python:username != \'Anonymous User\' and signup_name" '
            'tal:content="string:(Invited: ${signup_name})" /></li>')

        standard_template = get_standard_template(portal)
        tal = standard_template.read()
        if new_logout in tal:
            self.log.debug('Standard_template already updated')
        else:
            changed = False
            for tal_code in old_logout:
                if tal_code in tal:
                    tal = tal.replace(tal_code, new_logout)
                    changed = True
            if changed:
                standard_template.write(tal)
                self.log.debug('Standard_template updated')
            else:
                self.log.error('Old and new code not in standard_template')
                return False

        return True


class Eionet_2020(UpdateScript):
    title = ('Replace standard template with the one for eionet 2020 style')
    authors = ['Valentin Dumitru']
    creation_date = 'Mar 04, 2020'

    def _update(self, portal):
        layout_tool = portal.getLayoutTool()
        base_path = path.dirname(groupware_site.__file__)
        default_template = PageTemplateFile(
            base_path + '/skel/layout/groupware/standard_template.zpt')
        default_template.read()
        standard_template = get_standard_template(portal)
        standard_template.read()
        if standard_template._text == default_template._text:
            self.log.debug('Standard template already updated')
        else:
            standard_template.write(default_template._text)
            self.log.debug('Standard_template updated')

        if getattr(layout_tool.groupware, 'eionet_2020', None):
            self.log.debug('groupware 2020 scheme already present')
        else:
            skin_ob = layout_tool.groupware
            skel_handler = portal.get_skel_handler(base_path)
            diskpath_prefix = skel_handler.root.layout.diskpath_prefix
            skel_path = skel_handler.skel_path
            for skin in skel_handler.root.layout.skins:
                if skin.id == 'groupware':
                    break
            for scheme in skin.schemes:
                if scheme.id == 'eionet_2020':
                    if skin_ob._getOb(scheme.id, None):
                        skin_ob.manage_delObjects([scheme.id])
                    skin_ob.manage_addScheme(id=scheme.id,
                                             title=scheme.title)
                    scheme_ob = skin_ob._getOb(scheme.id)
                    for style in scheme.styles:
                        content = portal.futRead(
                            path.join(skel_path, 'layout', skin.id, scheme.id,
                                      '%s.css' % style.id),
                            'r')
                        if scheme_ob._getOb(style.id, None):
                            scheme_ob.manage_delObjects([style.id])
                        scheme_ob.manage_addStyle(
                            id=style.id, title=style.title, file=content)
                    for image in scheme.images:
                        content = portal.futRead(
                            path.join(skel_path, 'layout', skin.id, scheme.id,
                                      image.id),
                            'rb')
                        if not scheme_ob._getOb(image.id, None):
                            scheme_ob.manage_addImage(id=image.id, file='',
                                                      title=image.title)
                        image_ob = scheme_ob._getOb(image.id)
                        image_ob.update_data(data=content)
                        image_ob._p_changed = 1

                    for file in scheme.files:
                        content = portal.futRead(
                            path.join(skel_path, 'layout', skin.id, scheme.id,
                                      file.id),
                            'rb')
                        if not scheme_ob._getOb(file.id, None):
                            scheme_ob.manage_addFile(id=file.id, file='',
                                                     title=file.title)
                        file_ob = scheme_ob._getOb(file.id)
                        content_type = getattr(file, 'content_type', None)
                        file_ob.update_data(content, content_type)
                        file_ob._p_changed = 1

                    for diskfile in scheme.diskfiles:
                        manage_addDiskFile(scheme_ob, pathspec='/'.join([
                            diskpath_prefix,
                            'layout',
                            skin.id,
                            scheme.id,
                            diskfile.path]), id=(diskfile.id or ''))

                    for disktemplate in scheme.disktemplates:
                        manage_addDiskTemplate(
                            scheme_ob,
                            pathspec='/'.join([diskpath_prefix,
                                               'layout',
                                               skin.id,
                                               scheme.id,
                                               disktemplate.path]),
                            id=(disktemplate.id or ''))

            self.log.debug('groupware 2020 scheme added successfully')
        layout_tool.manageLayout('groupware', 'eionet_2020')
        self.log.debug('groupware 2020 scheme set as current scheme')

        return True


class Fix2020Style(UpdateScript):
    title = ('Fix CSS for eionet_2020 style')
    authors = ['Valentin Dumitru']
    creation_date = 'Dec 18, 2020'

    def _update(self, portal):
        old_css = (
            'form input, form select {\n'
            'border-radius: 15px !important;\n'
            'height: 27px !important;\n'
            'line-height: inherit !important;\n'
            'padding: 0 10px !important;\n'
            'border: 1px solid #dddddd !important\n'
            '}'
        )
        new_css = (
            'form input, form select {\n'
            'border-radius: 15px !important;\n'
            'line-height: inherit !important;\n'
            'padding: 0 10px !important;\n'
            'border: 1px solid #dddddd !important\n'
            '}\n'
            '\n'
            'form input {\n'
            'height: 27px !important;\n'
            '}'
        )

        style = portal.portal_layout.groupware.eionet_2020.gw_style_css
        css = style.read()
        if old_css in css:
            css = css.replace(old_css, new_css)
            style.write(css)
            self.log.debug('Style updated')
        else:
            self.log.debug('Style already updated')

        return True
