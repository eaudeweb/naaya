from Products.naayaUpdater.updates import UpdateScript, PRIORITY
from Products.naayaUpdater.updates.utils import get_standard_template

class UpdateSiteLogos(UpdateScript):
    """ """
    title = 'Adapt standard_template to the changes to site logos'
    creation_date = 'Oct 26, 2011'
    authors = ['Valentin Dumitru']
    priority = PRIORITY['HIGH']
    description = ('Layout tool now only serves on pair of site logos for all languages. The standard_templates are adapted to these changes.')

    def _update(self, portal):
        portal_layout = portal.getLayoutTool()

        self.update_standard_template(portal)
        self.update_logobis_to_right_logo_styles(portal_layout)
        self.log.debug('=' * 20)

        self.update_left_logo(portal_layout)
        self.log.debug('=' * 20)

        self.update_right_logo(portal_layout)
        self.log.debug('=' * 20)

        self.check_logos_after_update(portal_layout)
        return True

    def update_standard_template(self, portal):
        self.log.debug('Updating standard_template')
        standard_template = get_standard_template(portal)
        tal = standard_template.read()

        if 'here/leftLogoUrl' in tal:
            self.log.debug('before update here/leftLogoUrl in standard_template')
        else:
            self.log.debug('before update here/leftLogoUrl not in standard_template')
        if 'here/rightLogoUrl' in tal:
            self.log.debug('before update here/rightLogoUrl in standard_template')
        else:
            self.log.debug('before update here/rightLogoUrl not in standard_template')

        mapping = [
            # change to leftLogoUrl
            ('python:test(here.hasLeftLogo(), here.leftLogoUrl(), here.defaultLeftLogoUrl())', 'here/leftLogoUrl'),
            ('string:${here/getLayoutToolPath}/logo.gif', 'here/leftLogoUrl'),
            ('tal:condition="here/hasLeftLogo"', 'tal:condition="here/leftLogoUrl"'),
            # change to rightLogoUrl
            ('python:test(here.hasRightLogo(), here.rightLogoUrl(), here.defaultRightLogoUrl())', 'here/rightLogoUrl'),
            ('string:${here/getLayoutToolPath}/logobis.gif', 'here/rightLogoUrl'),
            ('string:${here/getLayoutToolPath}/logobis', 'here/rightLogoUrl'),
            ('tal:condition="here/hasRightLogo"', 'tal:condition="here/rightLogoUrl"'),
            # change right logo id
            ('id="logobis"', 'id="right_logo"'),
        ]
        changed = False
        for before, after in mapping:
            if before not in tal:
                continue
            tal = tal.replace(before, after)
            self.log.debug('changed to %r from %r', after, before)
            changed = True
        if changed:
            self.log.debug('standard_template changed')
            standard_template.write(tal)
        else:
            self.log.debug('standard_template not changed')

    def update_logobis_to_right_logo_styles(self, portal_layout):
        for obj in self.walk(portal_layout):
            if obj.__class__.__name__ != 'Style':
                continue
            data = obj.read()
            if '#logobis' not in data:
                continue
            obj.write(data.replace('#logobis', '#right_logo'))
            self.log.debug('replaced #logobis in %s', obj.absolute_url())

        for obj in self.walk(portal_layout):
            if not (obj.__class__.__name__ != 'File'
                    and obj.__name__.endswith('.css')):
                continue
            if '#logobis' not in obj.data:
                continue
            obj.data = obj.data.replace('#logobis', '#right_logo')
            self.log.debug('replaced #logobis in %s', obj.absolute_url())

    def walk(self, parent):
        for obj in parent.objectValues():
            yield obj
            if hasattr(obj.aq_base, 'objectValues'):
                for subobj in self.walk(obj):
                    yield subobj

    def update_left_logo(self, portal_layout):
        self.log.debug('Updating left logo from portal_layout')
        if getattr(portal_layout.aq_base, 'left_logo.gif', None):
            self.log.debug('left_logo.gif present in site')
            return

        self.log.debug('left_logo.gif not present, update needed')
        left_logo_ids = ['logo_en.gif', 'logo.gif', 'logo']
        for logo_id in left_logo_ids:
            old_logo = getattr(portal_layout.aq_base, logo_id, None)
            if old_logo and old_logo.data:
                portal_layout.manage_renameObjects([logo_id], ['left_logo.gif'])
                self.log.debug('%s renamed to left_logo.gif' % logo_id)
                return

    def update_right_logo(self, portal_layout):
        self.log.debug('Updating right logo from portal_layout')
        if getattr(portal_layout.aq_base, 'right_logo.gif', None):
            self.log.debug('right_logo.gif present in site')
            return

        self.log.debug('right_logo.gif not present, update needed')
        left_logo_ids = ['logobis_en.gif', 'logobis.gif', 'logobis']
        for logo_id in left_logo_ids:
            old_logo = getattr(portal_layout.aq_base, logo_id, None)
            if old_logo and old_logo.data:
                portal_layout.manage_renameObjects([logo_id], ['right_logo.gif'])
                self.log.debug('%s renamed to right_logo.gif' % logo_id)
                return

    def check_logos_after_update(self, portal_layout):
        left_logo = getattr(portal_layout.aq_base, 'left_logo.gif', None)
        right_logo = getattr(portal_layout.aq_base, 'right_logo.gif', None)
        if left_logo and right_logo:
            return
        if left_logo and not right_logo:
            self.log.warn("!!! No right logo after update")
        if not left_logo and right_logo:
            self.log.warn("!!! No left logo after update")
        if not left_logo and not right_logo:
            self.log.warn("!!! No left and no right logo after update")

        images = portal_layout.objectValues('Image')
        gifs_in_portal_layout = [ob.getId() for ob in images
                                        if '.gif' in ob.getId() and ob.data]
        if gifs_in_portal_layout:
            self.log.warn('The following not empty gifs are found in %s: %s',
                           portal_layout.absolute_url() + '/manage_workspace',
                           gifs_in_portal_layout)
        else:
            self.log.warn('No gifs in the portal_layout')
