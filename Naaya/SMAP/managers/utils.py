# The contents of this file are subject to the Mozilla Public
# License Version 1.1 (the "License"); you may not use this file
# except in compliance with the License. You may obtain a copy of
# the License at http://www.mozilla.org/MPL/
#
# Software distributed under the License is distributed on an "AS
# IS" basis, WITHOUT WARRANTY OF ANY KIND, either express or
# implied. See the License for the specific language governing
# rights and limitations under the License.
#
# The Initial Owner of the Original Code is SMAP Clearing House.
# All Rights Reserved.
#
# Authors:
#
# Alexandru Ghica
# Cornel Nitu
# Miruna Badescu

#Python imports
import locale
import operator
import zlib

def utZipText(text, level=6):
    """ 
        Zip string.
        Returns a tuple (zipstring, CRC).
        Level is an integer from 1 to 9 controlling the level of compression; 
            1 is fastest and produces the least compression, 
            9 is slowest and produces the most.
    """
    zobj = zlib.compressobj(level)
    zstr = zobj.compress(text)
    zstr += zobj.flush(zlib.Z_FINISH)

    #make CRC
    crc_check = zlib.crc32(text)
    return zstr, crc_check

def utUnZipText(zstr):
    """ 
        Unzip to string.
        Return a tuple (text, CRC).
    """
    #decompress
    text = zlib.decompress(zstr)
    #make CRC
    crc_check = zlib.crc32(text)
    return text, crc_check


def utSortObjsByLocaleAttr(p_list, p_attr, p_desc=1, p_locale=''):
    """Sort a list of objects by an attribute values based on locale"""
    if not p_locale:
        #normal sorting
        l_len = len(p_list)
        l_temp = map(None, map(getattr, p_list, (p_attr,)*l_len), xrange(l_len), p_list)
        l_temp.sort()
        if p_desc: l_temp.reverse()
        return map(operator.getitem, l_temp, (-1,)*l_len)
    else:
        #locale sorting based
        try:
            default_locale = locale.setlocale(locale.LC_ALL)

            try:
                #try to set for NT, WIN operating systems
                locale.setlocale(locale.LC_ALL, p_locale)
            except:
                #try to set for other operating system
                if p_locale == 'ar': p_locale = 'ar_DZ'
                else:                p_locale = '%s_%s' % (p_locale, p_locale.upper())
                locale.setlocale(locale.LC_ALL, p_locale)

            #sorting
            l_len = len(p_list)
            l_temp = map(None, map(getattr, p_list, (p_attr,)*l_len), xrange(l_len), p_list)
            l_temp.sort(lambda x, y: locale.strcoll(x[0], y[0]))
            if p_desc: l_temp.reverse()

            locale.setlocale(locale.LC_ALL, default_locale)
            return map(operator.getitem, l_temp, (-1,)*l_len)
        except:
            #in case of failure make a normal sorting
            locale.setlocale(locale.LC_ALL, default_locale)
            return utSortObjsByLocaleAttr(p_list, p_attr, p_desc)

def sync_two_selects():
    return """ 
        function dynamicSelect()
        {
            this.selects = new Array();
            
            this.addSelect = function(name)
            {
                this.selects[name] = new selectObj();
            }

            this.updateOptions = function(source, target)
            {
                var form = source.form;
                var target = form.elements[target];
                var value = source.options[source.selectedIndex].value;
                
                while(target.options.length) target.remove(0);
                
                if(!this.selects[source.name].options[value])
                {
                    //alert('Invalid selection.'); //For debugging while you set it up
                    return;
                }

                var data = this.selects[source.name].options[value].options;

                for(var x=0; x<data.length; x++)
                {
                    try
                    {
                        target.add(data[x]);
                    }
                    catch(e)
                    {
                        target.add(data[x], null);
                    }
                }
                //target.selectedIndex = 0;
            }
        }

        function selectObj()
        {
            this.options = new Array();
            
            this.addOption = function(value)
            {
                this.options[value] = new optionObj();
            }
        }

        function optionObj()
        {
            this.options = new Array();
            
            this.createOption = function(name, value)
            {
                this.options[this.options.length] = new Option(name, value);
            }
        }
"""