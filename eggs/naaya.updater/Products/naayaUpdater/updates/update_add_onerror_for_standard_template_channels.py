#Python imports
import re

#Zope imports
from AccessControl import ClassSecurityInfo

#Naaya imports
from Products.naayaUpdater.updates import UpdateScript, PRIORITY
from update_add_portlets_onerror_to_standard_template import get_standard_template
from utils import pat, physical_path

class UpdateAddOnerrorForStandardTemplateChannels(UpdateScript):
    """ Add on error for standard template channels """
    title = ' Add on error for standard template channels '
    creation_date = 'Dec 9, 2010'
    authors = ['Andrei Laza']
    priority = PRIORITY['LOW']
    description = ' Add on error for standard template channels '
    security = ClassSecurityInfo()

    security.declarePrivate('_update')
    def _update(self, portal):
        t = '%(info)s: <a href="%(url)s/manage_main">current skin standard template</a>'

        self.log.debug(physical_path(portal))
        standard_template = get_standard_template(portal)
        tal = standard_template.read()

        script_channels_start = '<tal:block repeat="channel python:here.getSite().getSyndicationTool().get_script_channels()">'
        script_channels_end = '</tal:block>'
        local_channels_start = '<tal:block repeat="channel python:here.getSite().getSyndicationTool().get_local_channels()">'
        local_channels_end = '</tal:block>'

        onerror_start = '<tal:block on-error="python:here.log_page_error(error)">'
        onerror_end = '</tal:block>'

        strs = []

        if re.search(pat(script_channels_start), tal) is not None:
            if re.search('%s\s*%s' % (pat(script_channels_start), pat(onerror_start)), tal) is None:
                pattern = '(\s*)%s((?:.|\n)*?)%s' % (pat(script_channels_start), pat(script_channels_end))
                replacement = '\\1%s\\1    %s\\2    %s\\1%s' % (script_channels_start, onerror_start, onerror_end, script_channels_end)
                tal = re.sub(pattern, replacement, tal)
                strs.append('changed script channels')
        else:
            strs.append("can't find script channels")

        if re.search(pat(local_channels_start), tal) is not None:
            if re.search('%s\s*%s' % (pat(local_channels_start), pat(onerror_start)), tal) is None:
                pattern = '(\s*)%s((?:.|\n)*?)%s' % (pat(local_channels_start), pat(local_channels_end))
                replacement = '\\1%s\\1    %s\\2    %s\\1%s' % (local_channels_start, onerror_start, onerror_end, local_channels_end)
                tal = re.sub(pattern, replacement, tal)
                strs.append('changed local channels')
        else:
            strs.append("can't find local channels")

        self.log.info(t % {'info': ','.join(strs),
                           'url': standard_template.absolute_url()})

        standard_template.write(tal)
        return True

