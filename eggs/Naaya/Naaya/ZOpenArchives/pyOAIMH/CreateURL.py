# -*- coding: iso-8859-15 -*-
#################################################################################
#										#
# Copyright (C) 2000-2003 Steve Giraud, Eric Brun, Benoit Charles,		#
# Alexandre Desoubeaux, Igor Barma, David McCuskey, Jean-Michel Cez    		#
# Christian Martel								#
#										#
# This program is free software; you can redistribute it and/or			#
# modify it under the terms of the GNU General Public License			#
# as published by the Free Software Foundation; either version 2		#
# of the License, or (at your option) any later version.			#
# This program is distributed in the hope that it will be useful,               #
# but WITHOUT ANY WARRANTY; without even the implied warranty of                #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the                 #
# GNU General Public License for more details.                                  #
#                                                                               #
# You should have received a copy of the GNU General Public License             #
# along with this program; if not, write to the Free Software      		#
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.   #
#										#
#################################################################################

class CreateURL:
    """
    class to format the URL query string
    """

    def __init__(self, args={}):
        """
        """
        self.dict = {}
        self.addProperty(args)


    def getURL(self):
        """
        return the structured URL
        """
        url = ""
        for prop in self.dict.keys():
            if self.dict[prop] == None:
                continue
            if url != "":
                url += "&"
            url += prop + "=" + self.dict[prop]

        return url
            

    def addProperty(self, args={}):
        """
        add a new property for the URL string
        """
        for prop in args.keys():
            self.dict[prop] = args[prop]
        

    def delProperty(self, names=[]):
        """
        """
        for prop in names:
            if self.dict.has_key(prop):
                del self.dict[prop]
        pass
