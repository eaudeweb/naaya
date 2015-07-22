#!/usr/bin/env python2.2

###########################################################################
#
# TextIndexNG                The next generation TextIndex for Zope
#
# This software is governed by a license. See
# LICENSE.txt for the terms of this license.
#
###########################################################################

import os, sys, re, traceback, atexit, time
from optik import OptionParser
import hotshot, hotshot.stats

import ZODB
from Products.TextIndexNG2 import TextIndexNG

try:
    import readline
    histfile = os.path.expanduser('~/.pyhist')
    readline.read_history_file(histfile)
    atexit.register(readline.write_history_file,histfile)
except: pass

class Doc:
    
    def __init__(self, txt, path=''):
        self.text = txt
        self.path = path
        self.meta_type = 'dummy'

    def getId(self):    return self.path

docs = dict()

def index_directory(dirname, extra, prof=0):

    if not dirname: raise RuntimeError,'no directory name'

    index = TextIndexNG.TextIndexNG('text', extra)

    files = os.listdir(dirname)
    files.sort()

    ts = time.time()
    bytes = 0
    print '-'*78

    for i in range(len(files)):
        f = files[i]
        print >>sys.stderr,f
        fname = os.path.join(dirname,f)
        bytes+=os.stat(fname)[6]
        if not os.path.isfile(fname): continue
        data = open(fname).read()

        doc = Doc(data, fname)
        docs[i] = doc

        if prof==1:
            prof = hotshot.Profile('tx.prof')
            retval = prof.runctx('index.index_object(i, doc)', globals(), locals())
            prof.close()
            stats = hotshot.stats.load('tx.prof')
            stats.strip_dirs()
            stats.sort_stats('cumulative')
            stats.print_stats(100)
        else:
            retval = index.index_object(i, doc)

        
    diff = time.time() - ts
    print "%d files, total size: %d" % (len(files), bytes)
    print "Indexing time: %5.3lf" % diff
    print 'Indexingspeed: %5.3lf KB/sec' % (1.0*bytes/diff/1024.0)

    return index

def interactive_mode(index, prof=0):

    while 1:
        line = raw_input("> ")

        try:
            if prof:
                prof = hotshot.Profile('tx.prof')
                resultset = prof.runctx('index._apply_index( {\'text\':{\'query\':line}})[0] ', globals(), locals())
                prof.close()
                stats = hotshot.stats.load('tx.prof')
                stats.strip_dirs()
                stats.sort_stats('cumulative')
                stats.print_stats(100)
            else:
                resultset  = index._apply_index( {'text':{'query':line}})[0] 

            print "Result: %d matches" % len(resultset)

            lst = list(resultset.items())
            lst.sort(lambda x,y : -cmp(x[1],y[1]))
            
            for docid,score in lst: 
                print  "%-2d %s %d" % (docid, docs[docid].getId(), score)
        except:
            traceback.print_exc()

if __name__== '__main__':

    usage = "Usage: %prog [options] "

    parser = OptionParser(usage=usage)
    parser.add_option('-d','--directory', action='store',type='string',
            dest='directory',help='directory to be search for input files')
    parser.add_option('-l','--left', action='store_true', 
            dest='extra_truncate_left', help='enable left truncation',default=0)
    parser.add_option('-n','--neardistance', action='store',type='int',
            dest='extra_near_distance',
            help='max. distance between words for near search',default=5)
    parser.add_option('-C','--converter', action='store',type='int',
            dest='extra_use_converters',
            help='use document converters',default=0)
    parser.add_option('-c','--casefolding', action='store_true',
            dest='extra_splitter_casefolding', help='enable casefolding',
            default=1)
    parser.add_option('-a','--autoexpand', action='store_true',
            dest='extra_autoexpand', help='auto expand',
            default=0)
    parser.add_option('-w','--stopwords', action='store',type='string',
            dest='extra_use_stopwords', help='name of stopword file')
    parser.add_option('-P','--parser', action='store', type='string',
            dest='extra_use_parser',default='PyQueryParser', 
            help='parser name')
    parser.add_option('-X','--prof', action='store_true',
            dest='prof',default=0,
            help='profiling on/off')

    options,args = parser.parse_args()

    class extra: 
        def __init__(self):
            self._keys = list()

        def set(self, k, v):
            setattr(self, k, v)
            self._keys.append(k)

        def keys(self): return self._keys

    E = extra()

    for k in dir(options):
        if k.startswith('extra_'):
            E.set(k[6:],getattr(options,k))

    index = index_directory(options.directory, E, options.prof)
    interactive_mode(index, options.prof)

