from AccessControl import ClassSecurityInfo

from Products.Naaya import NySite
from Products.naayaUpdater.updates import UpdateScript, PRIORITY
from Products.naayaUpdater import utils

class FillScriptBody(UpdateScript):
    """
    Fill Python Sripts which have empty bodies or no body at all

    """

    title = 'Fill Python Sripts which have empty bodies or no body at all'
    authors = ['Bogdan Tanase']
    creation_date = 'Jul 23, 2012'
    description = ("Python Scripts should always return an empty list if they "
    "their body is empty or they don't have body attribute")
    priority = PRIORITY['HIGH']
    security = ClassSecurityInfo()

    security.declarePrivate('_update')
    def _update(self, portal):
        syndication_tool = portal.getSyndicationTool()
        script_channels = syndication_tool.get_script_channels()

        for script in script_channels:
            try:
                body = script.body()
                if not body:
                    script.write('return []')
                    self.log.debug('Added body for %s Python Script',
                                   script.title_or_id())
                else:
                    self.log.debug('%s Python Script already has body',
                                   script.title_or_id())
            except AttributeError:
                script.write('return []')
                self.log.debug('Added body for %s Python Script',
                               script.title_or_id())

        return True
