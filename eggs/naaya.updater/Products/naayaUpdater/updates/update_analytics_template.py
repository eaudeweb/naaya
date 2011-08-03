import re

from Products.naayaUpdater.updates import UpdateScript

class UpdateAnalyticsTemplate(UpdateScript):
    """
    Converts site
    """
    title = 'Use Analytics Form'
    authors = ['Mihnea Simian']
    description = ('Convert portal layout and portal statistics to use '
                   'new analytics customizable form')
    creation_date = 'Aug 2, 2011'

    def get_uid(self, analytics_tool, std_tpl_tal):
        """
        Google Analytics ID can be found in two ways:
        * in script in portal statistics
        * in script hardcoded in standard_template in portal_layout
        Returns (ga_id0, ga_id1) where ga_id0 is search result in statistics
        and ga_id1 is search result in standard_template

        """
        # google is not very consistent with format, better be looser
        id_pat = re.compile(r'(UA-\d{4,10}-\d{1,3})')
        search_areas = (analytics_tool.ga_verify, std_tpl_tal)
        results = []
        for text in search_areas:
            match = id_pat.search(text)
            if match is not None:
                results.append(match.group())
            else:
                results.append('')

        return tuple(results)

    def _update(self, portal):
        analytics_tool = portal.getAnalyticsTool()
        std_template = portal.getLayoutTool().getCurrentSkin().standard_template
        std_tpl_tal = std_template.read()

        if getattr(analytics_tool, 'ga_id', None) is not None:
            self.log.debug('Portal already uses ID-property in portal statistics'
                           ' - Patched, skipping..')
            return True

        (ga_id_an, ga_id_std) = self.get_uid(analytics_tool, std_tpl_tal)
        if ga_id_an is ga_id_std is '':
            self.log.debug('No ID found, probably Google Analytics not in use')
            ga_id = ''
        elif ga_id_an != '' and ga_id_std != '' and ga_id_std != ga_id_std:
            self.log.error(('Two different IDs found: %s in statistics and %s'
                            ' in standard_template, using the first one')
                            % (ga_id_an, ga_id_std))
            ga_id = ga_id_an
        else:
            ga_id = ga_id_an or ga_id_std

        setattr(analytics_tool, 'ga_id', ga_id)
        delattr(analytics_tool, 'ga_verify')
        self.log.debug(('Deleted ga_verify and set ga_id to \'%s\' in '
                        'portal statistics') % ga_id)

        if ga_id_std:
            self.log.info('Manual action: remove analytics code from standard template')

        old_code = '<tal:block replace="structure here/portal_statistics/ga_verify" />'
        new_code = '<tal:block replace="structure python:here.rstk.google_analytics(here.portal_statistics.ga_id)" />'

        # delete old_code from std template customization
        # new one is already in head and can not be overwritten by customization
        if std_tpl_tal.find(old_code) > -1:
            std_tpl_tal = std_tpl_tal.replace(old_code, '')
            self.log.debug("Old Analytics tal successfully removed from standard template")
            std_template.write(std_tpl_tal)
        if std_tpl_tal.find(new_code) > -1:
            std_tpl_tal = std_tpl_tal.replace(new_code, '')
            self.log.debug("Redundant Analytics tal successfully removed from standard template")
            std_template.write(std_tpl_tal)

        return True
