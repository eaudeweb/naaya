from AccessControl import ClassSecurityInfo

from naaya.core.utils import force_to_unicode

from Products.naayaUpdater.updates import UpdateScript

class RemoveSiteTitle(UpdateScript):
    """ Remove site title attr """
    title = 'Remove site title attr'
    creation_date = 'Oct 19, 2011'
    authors = ['Andrei Laza']
    description = 'Remove site title attr if exists to use the local property.'
    security = ClassSecurityInfo()

    security.declarePrivate('_update')
    def _update(self, portal):
        if 'title' not in portal.aq_base.__dict__:
            self.log.debug('no need to update')
            return True

        lang = portal.gl_get_default_language()
        self.log.debug('default lang is %s' % lang)

        self.log.debug('portal.title = %r' % portal.title)

        localized_title_not_exists = 'title' not in portal._local_properties
        localized_title_empty = not portal.getLocalAttribute('title', lang)
        if localized_title_not_exists:
            self.log.debug("title localized property doesn't exist")
        if localized_title_empty:
            self.log.debug("title property empty for default lang")

        if localized_title_not_exists or localized_title_empty:
            portal.set_localpropvalue('title', lang,
                                        force_to_unicode(portal.title))
            self.log.debug("updated title localized property")

        delattr(portal.aq_base, 'title')
        self.log.debug('removed portal title attr')
        return True
