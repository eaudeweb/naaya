from Products.naayaUpdater.updates import UpdateScript, PRIORITY

channels = {}

channels['upcomingevents_rdf'] = """r, d = [], context.utGetTodayDate()
ra = r.append
for e in context.getCatalogedObjectsCheckView(meta_type='Naaya Event', approved=1):
    if e.start_date > d: ra(e)
return r
"""

channels['upcomingevents_rdf_replace'] = """r, d = [], context.utGetTodayDate()
ra = r.append
for e in context.getCatalogedObjectsCheckView(meta_type=['Naaya Event', 'Naaya Meeting'], approved=1):
    if e.start_date > d: ra(e)
return r
"""

channels['latestevents_rdf'] = """howmany = -1
if context.numberofitems != 0: howmany = context.numberofitems
return context.getCatalogedObjectsCheckView(meta_type='Naaya Event', approved=1, howmany=howmany)
"""

channels['latestevents_rdf_replace'] = """howmany = -1
if context.numberofitems != 0: howmany = context.numberofitems
return context.getCatalogedObjectsCheckView(meta_type=['Naaya Event', 'Naaya Meeting'], approved=1, howmany=howmany)
"""

channels['pastevents_rdf'] = """r, d = [], context.utGetTodayDate()
ra = r.append
for e in context.getCatalogedObjectsCheckView(meta_type='Naaya Event', approved=1):
    if e.start_date < d-1: ra(e)
return r
"""

channels['pastevents_rdf_replace'] = """r, d = [], context.utGetTodayDate()
ra = r.append
for e in context.getCatalogedObjectsCheckView(meta_type=['Naaya Event', 'Naaya Meeting'], approved=1):
    if e.start_date < d-1: ra(e)
return r
"""

class UpdateEventsSyndication(UpdateScript):
    title='Update events syndication channels to add Naaya Meeting'
    descrtiption = 'Naaya Meeting'
    priority = PRIORITY['HIGH']
    creation_date = 'Oct 29, 2010'
    authors = ['Alexandru Plugaru']

    def _update(self, portal):
        """ """
        channels_to_update = ['upcomingevents_rdf', 'latestevents_rdf',
                              'pastevents_rdf']
        if hasattr(portal, 'portal_syndication'):
            syn_tool = portal.portal_syndication
            self.log.debug("Updating %s/manage_main", syn_tool.absolute_url())
            for channel in channels_to_update:
                channel_ob = syn_tool._getOb(channel, None)
                if channel_ob is None:
                    self.log.debug("Missing %s", channel)
                    continue
                if not hasattr(channel_ob, 'body'):
                    self.log.debug("Wrong type %s", channel)
                    continue
                body = channel_ob.body().replace("\r", "")
                if body == channels[channel]:
                    channel_ob.write(channels[channel + '_replace'])
                    self.log.debug("Updated %s", channel_ob.absolute_url())
                else:
                    self.log.debug("Missmatch (update manually) %s/manage_main",
                                   channel_ob.absolute_url())
        return True
