###########################################################################
#
# TextIndexNG                The next generation TextIndex for Zope
#
# This software is governed by a license. See
# LICENSE.txt for the terms of this license.
#
###########################################################################

""" 
A simple timer class

$Id: Timer.py,v 1.5 2003/07/09 17:33:47 ajung Exp $
"""

import time

class Timer:
    """ simple timer class for profiling """

    def __init__(self, verbose=1):
        self.ts = time.time()
        self.verbose = verbose
        self.d = {}

    def __call__(self,s):
        diff = time.time() - self.ts
        self.ts = time.time()

        self.d[s] = diff

        if self.verbose:
            print "%s: %5.5lf" % (s,  diff)

    def printStats(self):

        total = 0.0
        for t in self.d.values(): total=total + t

        keys = self.d.keys()
        keys.sort()

        print "total: %5.5lf secs" % total
        for k,v in self.d.items():
            print "%-20s  %5.5lf secs   (%5.2lf %%) " % (k,v,100.0*v/total)    

