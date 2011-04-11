from Products.naayaUpdater.updates import UpdateScript

class UpdateGlossaries(UpdateScript):
    """  """
    title='A quick fix for Naaya Glossary and Naaya Thesaurus'
    description="Add `parent_anchors` attribute if none present to the glossary"

    def _update(self, portal):
        """ """

        for ob in portal.objectValues(['Naaya Glossary', 'Naaya Thesaurus']):
            if not hasattr(ob, 'parent_anchors'):
                self.log.info("Set parent_anchors to 0 for %s" %
                              ob.absolute_url())
                ob.parent_anchors = 0
                ob._p_changed = True
        return True
