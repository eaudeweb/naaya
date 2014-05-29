from Products.naayaUpdater.updates import UpdateScript

class UpdateUpcomingEvents(UpdateScript):
    title = ('Update upcoming events portlet to display event type')
    authors = ['Valentin Dumitru']
    creation_date = 'Jan 29, 2014'

    def _update(self, portal):
        old_tal = [('<a tal:attributes="href item/absolute_url" '
                    'tal:content="item/title_or_id">item</a>\t\n\t\t'
                    '<div tal:content="structure item/description" />'),
                    ('<a tal:attributes="href item/absolute_url" '
                    'tal:content="item/title_or_id">item</a>\t\r\n\t\t'
                    '<div tal:content="structure item/description" />')]
        new_tal = ('<a tal:attributes="href item/absolute_url" '
                      'tal:content="item/title_or_id">item</a>\n'
                      '<tal:block define="schema python:here.getSite()'
                      '.portal_schemas.NyEvent;\n\t\t\t\t\t\t\t\t\t\t'
                      "selection_list python:schema['event_type-property']"
                      '.get_selection_list();\n\t\t\t\t\t\t\t\t\t\t'
                      'our_items python:[list_item.title for list_item in '
                      'selection_list if list_item.id == item.event_type]">\n'
                      '\t\t<div tal:repeat="event our_items" tal:content="event" />\n'
                      '\t</tal:block>\n'
                      '\t<div tal:content="structure item/description" />')

        upcoming_events = portal.portal_portlets.portlet_upcomingevents_rdf
        tal = upcoming_events.read()
        if new_tal in tal:
            self.log.debug('Upcoming events portlet already updated')
        else:
            changed = False
            for tal_code in old_tal:
                if tal_code in tal:
                    tal = tal.replace(tal_code, new_tal)
                    changed = True
            if changed:
                upcoming_events.write(tal)
                self.log.debug('Upcoming events portlet updated')
            else:
                self.log.error('Old and new code not in Upcoming events portlet')
                return False

        return True
