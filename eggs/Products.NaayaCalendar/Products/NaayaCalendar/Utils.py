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
# Portions created by EEA are
# Copyright (C) European Environment Agency.  All
# Rights Reserved.
#
# Authors:
#
# Alex Ghica, Finsiel Romania

__version__='$Revision: 1.26 $'[11:-2]

# python imports
import string

# Zope imports


class Utils:
    """ utils """

    def __init__(self):
        """ constructor """
        pass

    def sortedDictByKey(self, p_dic):
        """ return sorted list of a dictionary values by its keys """
        l_keys = p_dic.keys()
        l_keys.sort()
        return [p_dic[key] for key in l_keys]

    def sortedKeysOfDict(self, p_dic):
        """ return the sorted list of a dictionary keys """
        if len(p_dic)==0:  return []
        l_keys = p_dic.keys()
        l_keys.sort()
        return l_keys

    def utGenerateList(self, p_index, p_list):
        """ creates a list according to a given index """
        while (p_index)>0:
            p_index -= 1
            p_list.append(p_list[0])
            p_list.remove(p_list[0])
        return p_list

    def utConvertLinesToList(self, value):
        """ takes a value from a textarea control and returns a list of values """
        if type(value) == type([]):
            return value
        elif value == '':
            return []
        else:
            return filter(lambda x:x!='', value.split('\r\n'))

    def utConvertListToLines(self, values):
        """ takes a list of values and returns a value for a textarea control """
        if len(values) == 0: return ''
        else: return '\r\n'.join(values)

    def getRange(self, p_range):
        """ return a range """
        return range(1, p_range+1)

    def getCounter(self, p_counter):
        """ return the counter """
        l_start_day = self.getDayIndex(self.start_day)
        if p_counter >= l_start_day:
            return p_counter - l_start_day
        else:
            return 7 - (l_start_day - p_counter)

    def getDaysMatrix(self, p_day_start, p_days_number):
        """ returns the matrix for day's display """
        l_matrix=[]
        l_item=[]
        for k in p_day_start:
            l_item.append('')
        for day in p_days_number:
            if (len(p_day_start) + int(day)) % 7 != 0 and day!=p_days_number[len(p_days_number)-1]:
                l_item.append(day)
            else:
                l_item.append(day)
                l_matrix.append(l_item)
                l_item=[]
        return self.utFillList(l_matrix)

    def utTestHasAttr(self, p_obj, p_meta):
        """ test if an object has a specific property """
        return hasattr(p_obj, p_meta[0]) and (p_meta[1]=='' or hasattr(p_obj, p_meta[1]))

    def utTestBobobase(self, p_string):
        """ test if a given string is equal with bobobase_modification_time """
        if p_string == 'bobobase_modification_time':  return 1
        return 0

    def utTestEmptyList(self, p_list):
        """ test if empty list """
        if len(p_list)==0 or (len(p_list)==1 and p_list[0]==''):  return 0
        return 1

    def utDayLength(self, p_length):
        """ return all day's name by length """
        sorted_weekdays = self.getLongWeekdaysSorted()
        if p_length == 'All':
            return self.utCombineList(sorted_weekdays, sorted_weekdays)

        l_days = [day[:int(p_length)] for day in sorted_weekdays]
        return self.utCombineList(l_days, sorted_weekdays)

    def utCombineList(self, p_f_list, p_s_list):
        """ from two lists makes a single list of tuple """
        l_index=0
        l_result=[]
        while l_index<7:
            l_result.append((p_f_list[l_index], p_s_list[l_index]))
            l_index=l_index+1
        return l_result


    def utEval(self, p_expr, p_obj):
        """ evaluates an expresion """
        try:
            return evalPredicate(p_expr, p_obj)
        except:
            return False

    #####################
    #   File Funtions   #
    #####################

    def utRead(self, p_path, p_flag='r'):
        """ read """
        return open(p_path, p_flag).read()


    #####################
    #   URL Functions   #
    #####################

    def utRemoveFromQS(self, list):
        """ returns a REQUEST.QUERY_STRING (using REQUEST.form,
            REQUEST.form=REQUEST.QUERY_STRING as a dictionary)
            without the pairs 'key=value' with 'key' in 'list' """
        out=''
        for key in self.REQUEST.form.keys():
            if key not in list:
                out=out+key+'='+str(self.REQUEST.form[key])+'&'
        out=out[:-1]
        return out

    #####################
    #   List Functions  #
    #####################

    def utFillList(self, l_list):
        """ fill the last list item from a list with empty spaces """
        p_list = l_list[len(l_list)-1]
        if len(p_list)<7:
            k=7-len(p_list)
            while k>0:
                k-=1
                p_list.append('')
        l_list[len(l_list)-1] = p_list
        return l_list



def evalPredicate(predicate, event):
    """Return the value of predicate for event; empty expressions evaluate to True.

        @param predicate: a predicate expression where self is the event,
                          e.g. "self.approved";
        @param event: event
    """
    if not predicate:
        return True
    return bool(eval(predicate,
                     {'__builtins__': __builtins__},
                     {'self': event}))
