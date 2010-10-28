import itertools
from Products.naayaUpdater.updates import UpdateScript

class UpdateWorkingLangs(UpdateScript):
    """  """
    title='Fix working langs in Naaya Semide Event and News'
    description="Fix lists such as ['E', 'N'] into ['EN']"

    def _update(self, portal):
        """ """
        for brain in portal.getCatalogTool()(
            meta_type=['Naaya Semide Event', 'Naaya Semide News']):

            ob = brain.getObject()
            if isinstance(ob.working_langs, basestring):
                ob.working_langs = [ob.working_langs]
                self.log.debug("Converting working_langs to list: %r",
                                       ob.absolute_url())
                ob._p_changed = True
            elif isinstance(ob.working_langs, (list, tuple)):
                if len(ob.working_langs) >= 2 and len(ob.working_langs[0]) == 1:
                    self.log.debug("Found broken working_langs: %r",
                                       ob.absolute_url())
                    if len(ob.working_langs) % 2 != 0:
                        self.log.debug("Language codes broken: %r",
                                       ob.absolute_url())
                        return False
                    it = iter(ob.working_langs)
                    ob.working_langs = map(''.join, itertools.izip(it, it))
                    ob._p_changed = True
        return True
