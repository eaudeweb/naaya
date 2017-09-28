from Products.naayaUpdater.updates import UpdateScript, PRIORITY

class UpdateUserManagementStyles(UpdateScript):
    title = 'Update Users management styles'
    creation_date = 'Nov 7, 2011'
    authors = ['Andrei Laza']
    priority = PRIORITY['LOW']
    description = 'Remove height from search box style.'

    def _walk(self, parent):
        for obj in parent.objectValues():
            yield obj
            if hasattr(obj.aq_base, 'objectValues'):
                for subobj in self._walk(obj):
                    yield subobj


    def process_content(self, data):
        SEARCH_BOX = '.search-box {'
        if SEARCH_BOX not in data:
            return None
        start = data.find(SEARCH_BOX)
        end_rel = data[start:].find('}')
        end = start + end_rel
        self.log.debug('Found search-box style at %r, %r, %r', start, end_rel, end)

        search_box = data[start:end]
        self.log.debug('content is %r', search_box)
        if 'height: 3.5em' not in search_box:
            return None

        search_box = search_box.replace('height: 3.5em;', '')
        self.log.debug('replacing content with: %r', search_box)
        return data[:start] + search_box + data[end:]


    def _update(self, portal):
        portal_layout = portal.portal_layout
        for obj in self._walk(portal_layout):
            if obj.__class__.__name__ != 'Style':
                continue
            self.log.debug(obj.absolute_url())
            new_data = self.process_content(obj.read())
            if new_data is None:
                continue
            obj.write(new_data)

        for obj in self._walk(portal_layout):
            if obj.__class__.__name__ != 'Template':
                continue
            self.log.debug(obj.absolute_url())
            new_data = self.process_content(obj.read())
            if new_data is None:
                continue
            obj.write(new_data)

        for obj in self._walk(portal_layout):
            if not (obj.__class__.__name__ == 'File'
                    and obj.__name__.endswith('.css')):
                continue
            self.log.debug(obj.absolute_url())
            new_data = self.process_content(obj.data)
            if new_data is None:
                continue
            obj.data = new_data
        return True
