""" Easily find and print all objects of a specified meta type """

from pprint import pprint as pp
from Products.Naaya.interfaces import INySite

HOST = 'http://forum.eionet.europa.eu'
METATYPES = ['Naaya TalkBack Consultation', 'Naaya Event', 'Naaya Meeting',
             'Naaya Mega Survey']

results = {}
for ob in app.objectValues():
    if INySite.providedBy(ob):
        catalog = ob.getCatalogTool()
        bfile_brains = catalog({'meta_type': METATYPES})
        for brain in bfile_brains:
            results.setdefault(brain.meta_type, []).append("%s%s" % (HOST, brain.getPath()))

pp(results)
