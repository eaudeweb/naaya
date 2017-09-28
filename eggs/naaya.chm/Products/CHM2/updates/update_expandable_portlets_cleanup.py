import re

from Products.naayaUpdater.updates import UpdateScript, PRIORITY
from Products.naayaUpdater.updates.utils import pat, get_standard_template

class UpdateExpandablePortletsCleanup(UpdateScript):
    """ """
    title = 'Cleanup expandable portlets code'
    creation_date = 'Aug 08, 2011'
    authors = ['Andrei Laza']
    priority = PRIORITY['HIGH']
    description = ('Remove ep_expanded_portlets code from standard_template')

    def _update(self, portal):
        standard_template = get_standard_template(portal)
        tal = standard_template.read()

        if 'epFromCookiesToSession' not in tal:
            self.log.debug('No need to update')
            return True

        self.log.debug('This portal needs update')

        chm_new_expandable = """
            <!--expandable portlets-->
            <tal:block replace="structure here/epFromCookiesToSession" />
            <tal:block replace='structure string:<script type="text/javascript">' />
                var ep_path = '<tal:block replace="python:here.absolute_url(1)" />'
                var ep_collapse_path = '<tal:block replace="string:${skin_files_path}/ep_collapse.gif" />'
                var ep_expand_path = '<tal:block replace="string:${skin_files_path}/ep_expand.gif" />'
            <tal:block replace='structure string:</script>' />
            <!--end expandable portlets-->
"""
        chm_new_expandable = pat(chm_new_expandable)
        chm_new_expandable = re.sub(' {4,}', '\s+', chm_new_expandable)

        chm_expandable = """
            <!--expandable portlets-->
            <tal:block replace="structure here/epFromCookiesToSession" />
            <tal:block replace='structure string:<script type="text/javascript">' />
                var ep_path = '<tal:block replace="python:here.absolute_url(1)" />'
                var ep_collapse_path = '<tal:block replace="string:${skin_files_path}/ep_collapse.gif" />'
                var ep_expand_path = '<tal:block replace="string:${skin_files_path}/ep_expand.gif" />'
                var expandedPortlet = ''
            <tal:block replace='structure string:</script>' />
            <script type="text/javascript" tal:attributes="src python:here.getLayoutTool().getCurrentSkin().absolute_url() + '/script_expandableportlets_js'"></script>
            <!--end expandable portlets-->
"""
        chm_expandable = pat(chm_expandable)
        chm_expandable = re.sub(' {4,}', '\s+', chm_expandable)


        chm_expandable2 = """
            <!--expandable portlets-->
            <tal:block replace="structure here/epFromCookiesToSession" />
            <tal:block replace='structure string:<script type="text/javascript">' />
                var ep_path = '<tal:block replace="python:here.absolute_url(1)" />'
                var ep_collapse_path = '<tal:block replace="string:${skin_files_path}/ep_collapse.gif" />'
                var ep_expand_path = '<tal:block replace="string:${skin_files_path}/ep_expand.gif" />'
            <tal:block replace='structure string:</script>' />
            <script type="text/javascript" tal:attributes="src python:here.getLayoutTool().getCurrentSkin().absolute_url() + '/script_expandableportlets_js'"></script>
            <!--end expandable portlets-->
"""
        chm_expandable2 = pat(chm_expandable2)
        chm_expandable2 = re.sub(' {4,}', '\s+', chm_expandable2)

        if re.search(chm_new_expandable, tal):
            self.log.debug('Replacing the chm_new expandable portlets tags')
            tal = re.sub(chm_new_expandable, '', tal, count=1)
        elif re.search(chm_expandable, tal):
            self.log.debug('Replacing the chm expandable portlets tags, version1')
            tal = re.sub(chm_expandable, '', tal, count=1)
        elif re.search(chm_expandable2, tal):
            self.log.debug('Replacing the chm expandable portlets tags, version2')
            tal = re.sub(chm_expandable2, '', tal, count=1)
        else:
            self.log.error("Can't match any expandable portlets tags")
            return False

        standard_template.write(tal)
        return True
