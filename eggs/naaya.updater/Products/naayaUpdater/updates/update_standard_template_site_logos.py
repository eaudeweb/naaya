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
        standard_template = get_standard_template(portal)
        tal = standard_template.read()
        changed = False

        if 'python:test(here.hasLeftLogo(), here.leftLogoUrl(), here.defaultLeftLogoUrl())' in tal:
            tal = tal.replace('python:test(here.hasLeftLogo(), here.leftLogoUrl(), here.defaultLeftLogoUrl())', 'here/leftLogoUrl', 1)
            self.log.debug('leftLogoUrl updated')
            changed = True
        if 'string:${here/getLayoutToolPath}/logo.gif' in tal:
            tal = tal.replace('string:${here/getLayoutToolPath}/logo.gif',
                    'here/leftLogoUrl', 1)
            self.log.debug('leftLogoUrl updated')
            changed = True
        if 'here/leftLogoUrl' in tal:
            self.log.debug('here/leftLogoUrl in standard_template')
        else:
            self.log.error('here/leftLogoUrl not in standard_template')

        if 'python:test(here.hasRightLogo(), here.rightLogoUrl(), here.defaultRightLogoUrl())' in tal:
            tal = tal.replace('python:test(here.hasRightLogo(), here.rightLogoUrl(), here.defaultRightLogoUrl())', 'here/rightLogoUrl', 1)
            self.log.debug('rightLogoUrl updated')
            changed = True
        if 'string:${here/getLayoutToolPath}/logobis' in tal:
            tal = tal.replace('string:${here/getLayoutToolPath}/logobis',
                    'here/rightLogoUrl', 1)
            self.log.debug('rightLogoUrl updated')
            changed = True
        if 'here/rightLogoUrl' in tal:
            self.log.debug('here/rightLogoUrl in standard_template')
        else:
            self.log.error('here/rightLogoUrl not in standard_template')

        if 'id="logobis"'in tal:
            tal = tal.replace('id="logobis"', 'id="right_logo"', 1)
            self.log.debug('id="right_logo" updated')
            changed = True

        if changed:
            standard_template.write(tal)

        portal_layout = portal.getLayoutTool()
        if not getattr(portal_layout.aq_base, 'left_logo.gif', None):
            self.log.debug('left_logo.gif not present, update needed')
            left_logo_ids = ['logo_en.gif', 'logo.gif', 'logo']
            for logo_id in left_logo_ids:
                old_logo = getattr(portal_layout.aq_base, logo_id, None)
                if old_logo and old_logo.data:
                    portal_layout.manage_renameObjects([logo_id],['left_logo.gif'])
                    self.log.debug('%s renamed to left_logo.gif' % logo_id)
                    break
            if not getattr(portal_layout.aq_base, 'left_logo.gif', None):
                self.log.error("!!! Expected left logo ids not found for renaming")
                gifs_in_portal_layout = [ob.getId() for ob in
                        portal_layout.objectValues('Image')
                        if '.gif' in ob.getId() and ob.data]
                if len(gifs_in_portal_layout) > 0:
                    self.log.error('Following not empty gifs are found in %s: %s' % (portal_layout.absolute_url()+'/manage_workspace', gifs_in_portal_layout))
                else:
                    self.log.error('No gifs in the portal_layout')
        else:
            self.log.debug('left_logo.gif present in site' % logo_id)


        if not getattr(portal_layout.aq_base, 'right_logo.gif', None):
            self.log.debug('right_logo.gif not present, update needed')
            left_logo_ids = ['logobis_en.gif', 'logobis.gif', 'logobis']
            for logo_id in left_logo_ids:
                old_logo = getattr(portal_layout.aq_base, logo_id, None)
                if old_logo and old_logo.data:
                    portal_layout.manage_renameObjects([logo_id],['right_logo.gif'])
                    self.log.debug('%s renamed to right_logo.gif' % logo_id)
                    break
            if not getattr(portal_layout.aq_base, 'right_logo.gif', None):
                self.log.error("!!! Expected right logo ids not found for renaming")
                gifs_in_portal_layout = [ob.getId() for ob in
                        portal_layout.objectValues('Image')
                        if '.gif' in ob.getId() and ob.data]
                if len(gifs_in_portal_layout) > 0:
                    self.log.error('Following not empty gifs are found in %s: %s' % (portal_layout.absolute_url()+'/manage_workspace', gifs_in_portal_layout))
                else:
                    self.log.error('No gifs in the portal_layout')
        else:
            self.log.debug('right_logo.gif present in site' % logo_id)

        return True
