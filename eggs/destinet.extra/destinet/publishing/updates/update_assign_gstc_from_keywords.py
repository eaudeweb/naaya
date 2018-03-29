import re
from Products.naayaUpdater.updates import UpdateScript


class AssignGSTCFromKeywords(UpdateScript):
    """
    Move GSTC Criteria infromation from keywords to property
    """
    title = 'Destinet: Move GSTC Criteria info from keywords to property'
    creation_date = 'Mar 28, 2018'
    authors = ['Valentin Dumitru']
    description = ('Iterates best practices, searches for GSTC keywords and '
                   'move these to the new property')

    def _update(self, portal):
        cat = portal.getCatalogTool()
        best_brains = cat.search({'meta_type': 'Naaya Best Practice'})
        for brain in best_brains:
            ob = brain.getObject()
            changed = 0
            if ob.geo_type != 'symbol818':
                ob.geo_type = 'symbol818'
                changed = 1
            for lang in portal.gl_get_languages():
                keywords = ob.getLocalProperty('keywords', lang)
                gstcs = re.findall('GSTCD[A-D][0-9]*', keywords)
                if gstcs:
                    changed = 1
                    if getattr(ob, 'gstc_criteria', ''):
                        ob.gstc_criteria = list(set(gstcs + ob.gstc_criteria))
                    else:
                        ob.gstc_criteria = gstcs
                    for gstc in gstcs:
                        keywords = ob.getLocalProperty('keywords', lang)
                        ob.set_localpropvalue(
                            'keywords', lang, keywords.replace(
                                '%s, ' % gstc, '').replace(
                                ', %s' % gstc, '').replace(
                                gstc, '')
                        )
            if changed:
                self.log.debug('%s updated' % ob.absolute_url())
                ob.recatalogNyObject(ob)

        return True
