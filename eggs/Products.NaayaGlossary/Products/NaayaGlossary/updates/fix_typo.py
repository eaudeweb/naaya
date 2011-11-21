from Products.naayaUpdater.updates import UpdateScript

class FixTypo(UpdateScript):
    title = 'Fix typo in CHM terms'
    authors = ('Stanciu Gabriel', 'Andrei Laza')
    creation_date = 'Aug 9, 2011'
    description = ('Change "Biodiversity and  tourism" to'
                  '"Biodiversity and tourism" for chm terms glossary')

    def _update(self, portal):
        ob = portal.chm_terms._getOb('04')._getOb('04_10')
        old_title = ob.title

        if ob.title == 'Biodiversity and  tourism':
            ob.title = ob.title.replace(' tourism', 'tourism')
            self.log.debug('"%s" is now: "%s"' % (old_title, ob.title))
        else:
            self.log.debug('No need to update')

        return True
