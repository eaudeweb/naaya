# -*- coding=utf-8 -*-

import operator

from AccessControl import ClassSecurityInfo
from Products.naayaUpdater.updates import UpdateScript, PRIORITY
from Products.naayaUpdater.utils import add_admin_entry

class UpdateCommentsAddSpamstatusProperty(UpdateScript):
    """ Add SPAM status property for existing comments """
    title = 'Add SPAM status property for existing Naaya Comments'
    authors = [u'Bogdan Tănase']
    description = ''
    creation_date = 'Mar 28, 2012'
    priority = PRIORITY['HIGH']
    security = ClassSecurityInfo()

    security.declarePrivate('_update')

    def _update(self, portal):
        commented = portal.getCommentedObjects()
        for ob in commented:
            container = ob._get_comments_container()
            if container:
                try:
                    comments_ids = map(operator.itemgetter('id'), container._objects)
                except AttributeError:
                    comment_ids = [comment_id for comment_id in container]

                for comment_id in comments_ids:
                        comment = container._getOb(comment_id)
                        if not hasattr(comment, 'spamstatus'):
                            comment.spamstatus = False
                            comment.recatalogNyObject(comment)

        return True