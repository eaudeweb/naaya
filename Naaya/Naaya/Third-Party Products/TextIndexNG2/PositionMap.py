###########################################################################
#
# TextIndexNG                The next generation TextIndex for Zope
#
# This software is governed by a license. See
# LICENSE.txt for the terms of this license.
#
###########################################################################

""" 
functions for checking positions of words in documents 

$Id: PositionMap.py,v 1.12 2003/07/09 17:33:47 ajung Exp $
"""


class PositionMap:
    """ position map for word positions inside a document """

    def __init__(self):
        self.map = []

    def append(self, word, poslst):
        self.map.append( (word, poslst) )

    def __str__(self):
        return '\n'.join([ '\t"%s": %s' % (w,lst) for w,lst in self.map ])

    __repr__ = __str__


    def checkPositionMapBidirectional(self, near_distance):
        """ check if a PositionMap represents a valid match for
            a near search (bidirectional search)
        """

        # a posMap is a list of tuples (word, IISet() ), where
        # the IISet is a list of posititions of that word inside 
        # one document

        min_poslst = None 
        valid_positions = []

        for word, poslst in self.map:

            if min_poslst:
                if len(poslst) < len(min_poslst):
                    min_poslst = poslst
            else:
                min_poslst = poslst


        for pos in min_poslst:

            # perform a range search over all position lists

            num = 0        
            for word, poslst in self.map:
                keys = poslst.keys( pos - near_distance, 
                                    pos + near_distance)
                if len(keys) > 0: num += 1

            if num == len(self.map):
                valid_positions.append(pos) 
        
        return valid_positions


    def checkPositionMapUnidirectional(self, near_distance):
        """ check if a PositionMap represents a valid match for
            a near search (unidirectional search)
        """

        # a posMap is a list of tuples (word, IISet() ), where
        # the IISet is a list of posititions of that word inside 
        # one document

        valid_positions = []
        min_poslst = None 

        for word, poslst in self.map:
            if min_poslst:
                if len(poslst) < len(min_poslst):
                    min_poslst = poslst
            else:
                min_poslst = poslst

        for pos in self.map[0][1]:

            # perform a range search over all position lists

            num = 0 
            for i in range(len(self.map)):
                word, poslst = self.map[i]       
                keys = poslst.keys( pos + i - near_distance, 
                                    pos + i + near_distance)
                if len(keys) > 0: num+=1

            if num == len(self.map):
                valid_positions.append(pos) 
        
        return valid_positions


