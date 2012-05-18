from Products.naayaUpdater.updates import UpdateScript

class UpdateRDFCalendarIndex(UpdateScript):
    title = "Update RDF Calendar's index"
    authors = ('Valentin Dumitru',)
    creation_date = 'May 18, 2012'
    description = ("Update the RDF Calendar's index so it no longer crashes "
        "if year is not provided.")

    def _update(self, portal):
        rdf_index = portal.portal_rdfcalendar.index_html
        html = rdf_index.read()
        mapping = [
            ('tal:condition="python:request.has_key(\'month\')"',
                'tal:condition="python:request.has_key(\'month\') and '
                'request.has_key(\'year\')"'),
            ('tal:condition="not:python:request.has_key(\'month\')"',
                'tal:condition="not:python:request.has_key(\'month\') and '
                'request.has_key(\'year\')"'),
        ]
        changed = False
        for before, after in mapping:
            if before not in html:
                continue
            html = html.replace(before, after)
            self.log.debug('changed to %r from %r', after, before)
            changed = True
        if changed:
            self.log.debug('RDF calendar index changed')
            rdf_index.write(html)
        else:
            self.log.debug('RDF calendar index not changed')
        return True
