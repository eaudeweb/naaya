from Products.naayaUpdater.updates import UpdateScript

class LocalChannels2Unicode(UpdateScript):
    title = 'Migrate local channels title and description to unicode strings'
    authors = ['Andrei Laza']
    creation_date = 'Nov 04, 2011'

    def _update(self, portal):
        def non_ascii_but_not_unicode(value):
            if not isinstance(value, basestring):
                return False

            if isinstance(value, unicode):
                return False

            try:
                unicode(value)
            except UnicodeDecodeError:
                return True
            else:
                return False

        syndication_tool = portal.getSyndicationTool()
        for item in syndication_tool.objectValues():
            if item.__class__.__name__ != 'LocalChannel':
                continue

            attrs_to_migrate = [attr for attr in ['title', 'description']
                    if non_ascii_but_not_unicode(getattr(item, attr))]

            if not attrs_to_migrate:
                continue

            self.log.debug("For %s migrare %r",
                            item.absolute_url(), attrs_to_migrate)
            for attr in attrs_to_migrate:
                try:
                    new_val = unicode(getattr(item, attr), encoding="utf-8")
                except UnicodeDecodeError:
                    self.log.error('Error on attribute %s', attr)
                    raise
                setattr(item, attr, new_val)
                self.log.debug('Changed attribute %s', attr)
        return True
