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

import string

bad_chars =  "£/'° ,;?!:()[]{}ÄÅÁÀÂÃäåáàâãÇçÉÈÊËÆéèêëæÍÌÎÏíìîïÑñÖÓÒÔÕØöóòôõøßÜÚÙÛüúùûÝýÿ="
good_chars = "________________AAAAAAaaaaaaCcEEEEEeeeeeIIIIiiiiNnOOOOOOooooooSssUUUUuuuuYYyyZz_"
TRANSMAP = string.maketrans(bad_chars, good_chars)

def processId(id):
    """ Retourne un identifiant valide """
    if id:
        newId = string.translate(id, TRANSMAP)
        if newId[0]=='_' and len(newId)==1:
            newId = 'a'
        elif newId[0]=='_' and len(newId)>1:
            newId = 'a' + newId[1:]

        if len(newId) > 1 and newId[-2:]=='__':
            newId = newId[:-2] +'_a'
                
        return newId

    return ''
