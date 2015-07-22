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
# The Original Code is RDFCalendar version 1.0.
#
# The Initial Owner of the Original Code is European Environment
# Agency (EEA).  Portions created by Finsiel Romania for EEA are
# Copyright (C) European Environment Agency.  All
# Rights Reserved.
#
# Contributor(s):
# Soren Roug, EEA
# Cornel Nitu, Finsiel Romania
# Rares Vernica, Finsiel Romania

__doc__ = """
        RDFCalendar product module.
        The RDFCalendar-Product is a event/meeting discoverer


$Id: RDFCalendar.py 9265 2007-07-02 16:57:33Z nituacor $
"""
__version__='$Revision: 1.27 $'[10:-2]

from OFS import Folder
from AccessControl import ClassSecurityInfo
from OFS.ObjectManager import ObjectManager
from OFS.PropertyManager import PropertyManager
from OFS import SimpleItem
from DateTime import DateTime
from os.path  import join
from ZPublisher import Request
from Acquisition import Implicit
from OFS.Cache import Cacheable

import Products
import string
import Globals
import calendar

_marker = []  # Create a new marker object

manage_addRDFCalendarForm=Globals.DTMLFile('dtml/RDFCalendar_addForm', globals())

def manage_addRDFCalendar(self, id, title='', first_day_week='Monday',
        week_day_len=3, REQUEST=None):
    """Add a new RDFCalendar object with id=title."""

    ob=RDFCalendar(id, title, first_day_week, week_day_len)
    ob.id = id
    self._setObject(id, ob)

    indexfile = open(join(Globals.package_home(globals()) , \
            'dtml','RDFCalendarIndex.dtml'))
    content = indexfile.read()
    indexfile.close()
    ob.manage_addDTMLMethod('index_html',
        title='Calendar Events', file=content)


    show_events_file = open(join(Globals.package_home(globals()) , \
            'dtml','RDFCalendar_dayevents.dtml'))
    content = show_events_file.read()
    show_events_file.close()
    ob.manage_addDTMLMethod('show_day_events',
        title='Show events for one day', file=content)

    if REQUEST is not None:
        return self.manage_main(self, REQUEST, update_menu=1)


class RDFCalendar(Implicit, Folder.Folder, PropertyManager, Cacheable):
    """The RDFCalendar-Product is a event/meeting discoverer"""

    meta_type = "RDF Calendar"
    product_name = "RDFCalendar"    #Used where?

    _properties=(
            {'id':'title',          'type':'string', 'mode':'w'},
            {'id':'first_day_week', 'type':'selection',
             'select_variable':'first_day_of_week', 'mode':'w'},
            {'id':'week_day_len',   'type':'int',    'mode':'w'},
    )

    manage_options = (ObjectManager.manage_options[0],) + (
            PropertyManager.manage_options + (
                {'label' : 'View',     'action' : 'index_html'},
                {'label' : 'CSS',    'action' : 'default_css'},
                {'label' : 'Calendar', 'action' : 'view_calendar'},
                {'label' : 'Update',   'action' : 'manage_updateChannels'},
                {'label' : 'Undo',     'action' : 'manage_undoForm'},)
               +SimpleItem.SimpleItem.manage_options
               +Cacheable.manage_options
                )

    # Create a SecurityInfo for this class. We will use this 
    # in the rest of our class definition to make security 
    # assertions.
    security = ClassSecurityInfo()

    security.setPermissionDefault('Update RDF Calendar',('Manager','Anonymous'))

    security.declareProtected('View', 'default_css')
    default_css = Globals.DTMLFile("dtml/default_css", globals())

    security.declareProtected('View', 'view_calendar')
    view_calendar = Globals.DTMLFile("dtml/viewCalendar", globals())

    security.declareProtected('View', 'show_monthly_events')
    show_monthly_events = Globals.DTMLFile("dtml/show_monthly_events", globals())

    security.declareProtected('View','show_events_list')
    show_events_list = Globals.DTMLFile("dtml/show_events_list", globals())

    security.declareProtected('View', 'show_rdf')
    show_rdf = Globals.DTMLFile("dtml/show_rdf", globals())

    def __str__(self): return self.index_html()
    def __len__(self): return 1

    security.declarePrivate('first_day_of_week')
    def first_day_of_week (self):
        day_opt = ['Monday','Sunday']
        if self.first_day_week == 0:
            return day_opt
        else:
            day_opt.reverse()
            return day_opt

    security.declareProtected('View management screens', 'all_meta_types')
    def all_meta_types(self):
        """return a filtered list of meta types"""

        f = lambda x: x['name'] in ('DTML Method','Page Template','RDF Summary',
            'Script (Python)','External Method')
        return filter(f, Products.meta_types)

    security.declareProtected('View','getYear')
    def getYear(self):
        """if REQUEST is None return current year"""

        if self.REQUEST.has_key("year") and self.REQUEST.year!=None:
            return int(self.REQUEST.year)
        else:
            return DateTime().year()

    security.declareProtected('View','getMonth')
    def getMonth(self):
        """if REQUEST is None return current month"""

        if self.REQUEST.has_key("month") and self.REQUEST.month!=None:
            return int(self.REQUEST.month)
        else:
            return DateTime().month()

    security.declareProtected('View','show_month')
    def show_month(self):
        """ Display arrows to previous and next months in
            HTML format as table row
        """
        month=self.getMonth()
        year=self.getYear()
        time_slice=2

        prev_month=month-1
        prev_year=year
        if prev_month==0:
            prev_month=12
            prev_year=year-1

        next_month=month+1
        next_year=year
        if next_month==13:
            next_month=1
            next_year=year+1

        other_qs=self.removeFromQS(['month', 'year'])
        if len(other_qs)>0:
            other_qs="%s&amp;" % other_qs

        arrowurl = self.REQUEST.URL0
        out = []
        out.append('<caption>')

        # Left arrow (allow to go back in time only wihtin <time_slice> years - to prevent indexing of infinite urls)
        if prev_year>=(DateTime().year()-time_slice) and prev_year<=(DateTime().year()+time_slice):
            out.append('<a href="%s?%smonth=%s&amp;year=%s" title="previous month" class="nav">&laquo;</a>' % (arrowurl, other_qs, str(prev_month), str(prev_year)))

        # Current month/year
        out.append('<a href="%s/index_html?cal=1&amp;month=%s&amp;year=%s">%s %s</a>' % (self.absolute_url(), str(month), str(year), calendar.month_name[month], str(year)))

        # Right arrow (allow to go further in time only within <time_slice> years - to prevent indexing of infinite urls)
        if next_year<=(DateTime().year()+time_slice) and next_year>=(DateTime().year()-time_slice):
            out.append('<a href="%s?%smonth=%s&amp;year=%s" title="next month" class="nav">&raquo;</a>' % (arrowurl, other_qs, str(next_month), str(next_year)))

        out.append('</caption>')
        return ''.join(out)

    security.declareProtected('View','show_week')
    def show_week (self):
        """ display week days in HTML format as table row"""
        out=[]
        out.append('<tr>')
        for day in self.get_weekheader(self.week_day_len):
            out.append('<th scope="col" title="%s" abbr="%s">%s</th>' % (day[1].lower(), day[1], day[0]))
        out.append('</tr>\n')
        return ''.join(out)

    security.declareProtected('View','get_weekheader')
    def get_weekheader(self, p_week_day_len):
        """. return the days of week """
        l_result = []
        for l_day in string.split(calendar.weekheader(9)):
            l_result.append((l_day[:p_week_day_len], l_day))
        return l_result

    security.declareProtected('View','get_days_events')
    def get_days_events(self):
        """ search in objects with meta_type='RDF Summary'
            and return day_events list"""

        day_events = []
        for item in self.get_events(year=self.getYear(), month=self.getMonth()):
            if item.has_key('enddate'):
                interval = int(DateTime(item['enddate']) - \
                               DateTime(item['startdate']))
                if interval == 0:
                    if DateTime(item['startdate']).Date() not in day_events:
                        day_events.append(DateTime(item['startdate']).Date())
                else:
                    for i in range(interval+1):
                        if DateTime(int(DateTime(item['startdate'])+i)).Date() not in day_events:
                            day_events.append(DateTime(int(DateTime(item['startdate'])+i)).Date())
            else:
                if DateTime(item['startdate']).Date() not in day_events:
                    day_events.append(DateTime(item['startdate']).Date())
        return day_events

    security.declareProtected('View','get_events')
    def get_events(self, year=None, month=None, day=None):
        """ search in objects with meta_type='RDF Summary' and return events
            list with events going on in given 'month' and 'year'
        """
        # Retrieve the value from the cache.
        keyset = None
        if self.ZCacheable_isCachingEnabled():
            # Strange; I can't just use args
            keyset = { 'year':year, 'month':month, 'day':day }
            # Prepare a cache key.
            results = self.ZCacheable_get(view_name='get_events',
                 keywords=keyset, default=_marker)
            if results is not _marker:
                return results

        events = []
        for object in self.objectValues('RDF Summary'):
            for item in object.items():
                if not item.has_key('startdate') or item['startdate'] == '':
                    continue
                try:
                    startdate=DateTime(item['startdate'])
                except:
                    continue
                if item.has_key('enddate') and item.get('enddate', '').strip() != '':
                    enddate=DateTime(item['enddate'])
                else:
                    enddate=startdate
                if not year:
                    year1=startdate.year()
                    year2=enddate.year()
                else:
                    year1=year2=year
                if not month:
                    month1=startdate.month()
                    month2=enddate.month()
                else:
                    month1=month2=month
                if not day:
                    day1=1
                    day2=calendar.monthrange(year2,month2)[-1]
                else:
                    day1=day2=day
                enddate=enddate.Date()
                startdate=startdate.Date()
                date1=DateTime("%s/%s/%s" % (str(year1), str(month1), str(day1))).Date()
                date2=DateTime("%s/%s/%s" % (str(year2), str(month2), str(day2))).Date()
                if (startdate<=date1 and enddate>=date1) or \
                   (startdate>=date1 and enddate<=date2) or \
                   (startdate<=date2 and enddate>=date2) or \
                   (startdate<=date1 and enddate>=date2):
                    events.append(item)

        if keyset is not None:
            if events is not None:
                self.ZCacheable_set(events,view_name='get_events', keywords=keyset)
        return events

    security.declareProtected('View','show_days')
    def show_days(self):
        """ display days in HTML format as table rows"""

        list_day_events = self.get_days_events()
        days = []
        for week in calendar.monthcalendar(self.getYear(), self.getMonth()):
            days.append('<tr>\n ')
            day_number = 0
            for day in week:
                l_headers = self.get_weekheader(9)[day_number][0]
                curr_date = "%s/%s/%s" % (str(self.getYear()), string.zfill(str(self.getMonth()),2), string.zfill(str(day),2))
                if day == 0:
                    days.append('<td>')
                elif DateTime(curr_date).isCurrentDay():
                    days.append('<td class="today">')
                else:
                    days.append('<td>')

                if day==0:
                    days.append('&nbsp;</td>\n')
                    day_number += 1
                    continue

                if curr_date in list_day_events:
                    days.append('<a href="%s/show_day_events?date=%s">%s</a></td>' % (self.absolute_url(), curr_date, str(day)))
                else:
                    days.append('%s</td>' % str(day))
                day_number += 1
            days.append('</tr>\n')
        return ''.join(days)

    security.declareProtected('View','show_calendar')
    def show_calendar(self):
        """ display the calendar """
        return '<table id="calendar" cellspacing="0" cellpadding="0" summary="This month\'s calendar">%s%s%s</table>' % (self.show_month(), self.show_week(), self.show_days())

    security.declarePrivate('removeFromQS')
    def removeFromQS(self, list):
        """ returns a REQUEST.QUERY_STRING (using REQUEST.form,
            REQUEST.form=REQUEST.QUERY_STRING as a dictionary)
            without the pairs 'key=value' with 'key' in 'list' """

        out=""
        for key in self.REQUEST.form.keys():
            if key not in list:
                out="%s%s=%s&" % (out, key, str(self.REQUEST.form[key]))
        out=out[:-1]
        return out

    def __init__(self, id, title='', first_day_week=0,
            week_day_len=3, REQUEST=None):
        """ initialize a new instance of RDFCalendar """

        self.id = id
        self.title = title
        if first_day_week == 'Monday':
            self.first_day_week = 0
        else:
            self.first_day_week = 6
        self.week_day_len = week_day_len
        calendar.setfirstweekday(self.first_day_week)

    security.declareProtected('Change RDF Calendar','manage_designProperties')
    def manage_designProperties(self, REQUEST=None):
        """ Manage the design properties """
        self.cal_css=self.REQUEST.CALCSS
        if REQUEST is not None:
            return Globals.MessageDialog(title = 'Edited',
             message = "The properties of %s have been changed!" % self.id,
             action = self.REQUEST.HTTP_REFERER,
            )

    security.declareProtected('Change RDF Calendar','manage_editProperties')
    def manage_editProperties(self,first_day_week,REQUEST=None):
        """ Manage the edited values """

        if first_day_week == 'Monday':
            calendar.setfirstweekday(0)
        else:
            calendar.setfirstweekday(6)
        self.ZCacheable_invalidate()
        return PropertyManager.manage_editProperties(self,REQUEST)

    security.declareProtected('Update RDF Calendar','manage_updateChannels')
    def manage_updateChannels(self,REQUEST=None):
        """ Update all RDF channels"""

        msg=[]
        for object in self.objectValues('RDF Summary'):
            try:
                object.update()
                msg.append('Content of <strong>%s</strong> channel has been updated.' % object.id + '<br />')
            except:
                msg.append('<font color="red">' + \
                 'Error updating channel <strong>%s</strong>' % object.id + \
                 '</font>'+'<br />')
        self.ZCacheable_invalidate()
        if REQUEST is not None:
            return Globals.MessageDialog(title='Updated', 
             message=''.join(msg),action ='manage_main',)

# Initialize the class in order the security assertions be taken into account
Globals.InitializeClass(RDFCalendar)
