###########################################################################
#
# TextIndexNG                The next generation TextIndex for Zope
#
# This software is governed by a license. See
# LICENSE.txt for the terms of this license.
#
###########################################################################

import os, sys, hotshot, time, hotshot.stats

__file__ = os.path.abspath(sys.argv[0])
NAME = 'txngbench'

class Args:
    """ TextIndexNG argument class """

    def __init__(self, **kw):
        self.__dict__.update(kw)

    def keys(self):
        return self.__dict__.keys()

def setup_catalog():

    if NAME in app.objectIds():
        app.manage_delObjects(NAME)
    app.manage_addProduct['ZCatalog'].manage_addZCatalog(NAME, NAME)

    cat = app[NAME]
    args = Args(use_storage='StupidStorage')
    cat.manage_addIndex('PrincipiaSearchSource', 'TextIndexNG2', extra=args)
    return cat

def setup_texts(catalog):
    """ import texts from 'texts' folder as DTML Document """

    from OFS.DTMLDocument import addDTMLDocument

    dirname = os.path.join(os.path.dirname(__file__), 'texts')
    files = os.listdir(dirname)
    num_files = 0
    for f in files:
        fname = os.path.join(dirname, f)
        if not os.path.isfile(fname): continue
        fp = open(fname) 
        addDTMLDocument(catalog, id=f, title=f, file=fp)
        fp.close()
        num_files+=1


def index_texts(catalog, objs):
    """ index imported texts """

    print 'start'
    for obj in objs:
        print obj.absolute_url()
        catalog.catalog_object(obj, obj.absolute_url(1))
    print 'stop'

    get_transaction().commit()
    print 'done'

CAT = setup_catalog()
setup_texts(CAT)


objs = [o for o in CAT.objectValues('DTML Document') if o.getId().endswith('txt')]
        
print len(objs), 'objects to be indexed'
prof = hotshot.Profile('textindexng.prof')
ts = time.time()
prof.runcall(index_texts, CAT, objs)
te = time.time()
print 'Indexing terminated (Duration: %5.3f seconds, %5.5f seconds/document)' % ((te-ts), (te-ts)/len(objs))
stats = hotshot.stats.load('textindexng.prof')
stats.strip_dirs()
stats.sort_stats('cumulative')
#        stats.sort_stats('time', 'calls')
stats.print_stats(25)

