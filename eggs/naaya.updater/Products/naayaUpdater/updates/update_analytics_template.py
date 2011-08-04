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

    # google is not very consistent with format, better be looser
    id_pattern = re.compile(r'(UA-\d{4,10}-\d{1,3})')

    def get_uid(self, analytics_tool, std_tpl_tal):
        """
        Google Analytics ID can be found in two ways:
        * in script in portal statistics
        * in script hardcoded in standard_template in portal_layout
        Returns (ga_id0, ga_id1) where ga_id0 is search result in statistics
        and ga_id1 is search result in standard_template

        """
        search_areas = (analytics_tool.ga_verify, std_tpl_tal)
        results = []
        for text in search_areas:
            match = self.id_pattern.search(text)
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
            self.log.info('MANUAL action: remove analytics code from standard template')

        old_code = '<tal:block replace="structure here/portal_statistics/ga_verify" />'
        new_code = '<tal:block replace="structure python:here.rstk.google_analytics(here.portal_statistics.ga_id)" />'

        # clean up any codes
        if std_tpl_tal.find(old_code) > -1:
            std_tpl_tal = std_tpl_tal.replace(old_code, '')
            self.log.debug("Old Analytics tal successfully removed from standard template")
        if std_tpl_tal.find(new_code) > -1:
            std_tpl_tal = std_tpl_tal.replace(new_code, '')
            self.log.debug("Redundant Analytics tal successfully removed from standard template")

        # special case - complete std template overwritten, need to place code
        if std_tpl_tal.find('</head>') > -1:
            # try to keep indentation
            std_tpl_tal = re.sub(r'([ \t]*)</head>',
                                 r'\1' + new_code + r'\n\1</head>', std_tpl_tal)

        std_template.write(std_tpl_tal)

        # check script appears once (or doesn't appear if id not configured)
        frm = portal.getFormsTool().getForm('site_search')
        try:
            portal.REQUEST.PARENTS[0] = portal
            html = frm.__of__(portal)()
        except Exception, e:
            self.log.debug("Can not test, can not render site_index")
            return True
        else:
            found = self.id_pattern.findall(html)
            expected = int(ga_id != '') + int(ga_id_std != '')
            if len(found) == expected:
                self.log.debug(("%d occurences (%r) of UA-numbers found in "
                                "site_index, as EXPECTED") % (len(found), found))
                return True
            else:
                self.log.error(("%d UNEXPECTED occurences(%r) of UA-numbers "
                                "found in site_index, %d were expected")
                               % (len(found), found, expected))
                return False
