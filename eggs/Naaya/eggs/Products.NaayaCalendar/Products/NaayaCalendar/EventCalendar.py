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

__version__='$Revision: 1.38 $'[11:-2]

# python imports
from os.path import join
import calendar

# Zope imports
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import view_management_screens, view
from OFS.Folder import Folder
from OFS.Image import manage_addImage, Image
import OFS
from Globals import InitializeClass, package_home
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
import Products
from DateTime import DateTime

# product imports
from DateFunctions import DateFunctions
from Utils import Utils, evalPredicate

# constants
css_calendar_default = {'border-weight':'2', 'border-color':'#cccccc', 'width':'160', 'height':'150', 'font-family':'Arial, Helvetica, Sans-Serif', \
                'title-font-color':'#000000', 'title-background':'#f0f0f0', 'title-font-size':'100', \
                'month-background':'#ffffff', 'month-font-size':'90', 'month-image-height':'1', 'month-image-width':'1', \
                'week-background':'#f0f0f0', 'week-font-size':'90', 'week-font-color':'#000000', \
                'day-background':'#ffffff', 'day-font-size':'90', 'day-font-color':'#000000', 'day-border-color':'#cccccc', 'day-border-weight':'0', 'day-padding':'2', \
                'today-background':'#f0f0f0', 'today-font-color':'#6699cc', 'today-border-color':'#cccccc', 'today-border-weight':'1', \
                'event-background':'#f0f0bb', 'event-font-color':'blue', 'event-border-color':'#cccccc', 'event-border-weight':'1'}

css_events_default = {'table-font-size':'90', 'title-font-color':'#000000', \
              'menu-font-color':'#000000', 'item-border-color':'#f0f0f0'}


manage_addEventCalendar_html = PageTemplateFile('zpt/calendar_add', globals())

def manage_addEventCalendar(self, id, title='', description='',
                            day_len='', cal_meta_types='', start_day='Monday',
                            catalog='', REQUEST=None):
    """ Adds a new EventCalendar object """
    ob = EventCalendar(id, title, description, day_len, cal_meta_types, start_day, catalog)
    self._setObject(id, ob)
    l_meta_types = ob.cal_meta_types
    ob.cal_meta_types = {}
    ob.cal_meta_types = ob.setCalMetaTypes(l_meta_types)
    #loads default css
    ob.css_calendar = css_calendar_default
    ob.css_events = css_events_default
    if REQUEST is not None:
        return self.manage_main(self, REQUEST, update_menu=1)


class EventCalendar(Folder, DateFunctions, Utils): # TODO: inherit only from Folder
    """ Event calendar """

    meta_type = 'Naaya Calendar'
    product_name = 'Naaya Calendar'

    manage_options =((Folder.manage_options[0],) +
                     ({'label':'Properties',     'action':'manage_properties'},
                      {'label':'View',            'action':'index_html'},
                      {'label':'Calendar style',  'action':'manage_style_calendar'},
                      {'label':'Events style',    'action':'manage_style_events'},
                      {'label':'Calendar',        'action':'show_calendar'},
                      {'label':'Undo',            'action':'manage_UndoForm'},) +
                     (Folder.manage_options[3],))

    security = ClassSecurityInfo()

    def __init__(self, id, title, description, day_len, cal_meta_types, start_day, catalog):
        """ constructor """
        self.id =               id
        self.title =            title
        self.description =      description
        self.day_len =          day_len
        self.cal_meta_types =   cal_meta_types
        self.start_day =        start_day
        self.catalog =          catalog

    def __str__(self):  return self.index_html()

    def all_meta_types(self):
        """ What can you put inside me? """
        local_meta_types = []
        f = lambda x: x['name'] in ('Page Template', 'Script (Python)', 'File', 'Folder', 'DTML Method', 'Image')
        for x in filter(f, Products.meta_types):
            local_meta_types.append(x)
        return local_meta_types

    security.declareProtected(view_management_screens, 'manage_afterAdd')
    def manage_afterAdd(self, item, container):
        """ after add event """
        try:
            content = self.utRead(join(package_home(globals()), 'www', 'left_arrow.gif'), 'rb')
            manage_addImage(self, id='left_arrow', title='', file='')
            img_ob = self._getOb('left_arrow')
            img_ob.update_data(data=content)
        except:
            pass

        try:
            content = self.utRead(join(package_home(globals()), 'www', 'right_arrow.gif'), 'rb')
            manage_addImage(self, id='right_arrow', title='', file='')
            img_ob = self._getOb('right_arrow')
            img_ob.update_data(data=content)
        except:
            pass

        try:
            from Products.PageTemplates.ZopePageTemplate import manage_addPageTemplate
            style_css = open(join(package_home(globals()), 'zpt', 'calendar_style_css.zpt'))
            content = style_css.read()
            style_css.close()
            manage_addPageTemplate(self, id='calendar_style', title='Calendar CSS file', text=content)
        except:
            pass

        Folder.inheritedAttribute('manage_afterAdd')(self, item, container)


    #############
    #   GETTERS #
    #############

    security.declareProtected(view, 'getParent')
    def getParent(self):
        """ return parent """
        return self.aq_inner.getParentNode()

    security.declareProtected(view, 'getEventCalendar')
    def getEventCalendar(self):
        """ return self """
        return self

    security.declareProtected(view, 'getEventCalendarURL')
    def getEventCalendarURL(self):
        """ return the absolute_url """
        return self.absolute_url()

    security.declareProtected(view, 'getSortedMetaTypes')
    def getSortedMetaTypes(self):
        """ sorts the meta_type list """
        return self.sortedKeysOfDict(self.cal_meta_types) # TODO: use sorted in newer Pythons

    security.declareProtected(view, 'getCalMetaTypes')
    def getCalMetaTypes(self):
        """ convert to lines the meta_type list"""
        return self.utConvertListToLines(self.getSortedMetaTypes())

    security.declareProtected(view, 'getArrowURL')
    def getArrowURL(self):
        """ return the arrow's URL """
        other_qs=self.utRemoveFromQS(['cmonth', 'cyear'])
        if len(other_qs)>0:
            other_qs=other_qs+"&"
        return self.utURL() + "?" + other_qs

    security.declareProtected(view, 'getIndexURL')
    def getIndexURL(self):
        """ return the month's URL """
        return self.getEventCalendarURL() + '/index_html?'

    security.declareProtected(view, 'getDaysURL')
    def getDaysURL(self):
        """ return the day's URL """
        return self.getEventCalendarURL() + '/day_events?'


    #########################
    #   EVENTS FUNCTIONS    #
    #########################
    security.declareProtected(view, 'getEvents')
    def getEvents(self, year, month, day=None):
        """Return the events for the specified date or the whole month if day
            is not specified.
        """
        if day:
            dates = [DateTime(year, month, day)]
        else:
            dates = [DateTime(year, month, day)
                        for day in range(1, calendar.monthrange(year, month)[1] + 1)]

        events = []
        catalog = self.unrestrictedTraverse(self.catalog)
        items = {}
        for date in dates:
            for meta_type, (interval_idx, predicate) in self.cal_meta_types.items():
                start_date_attr = catalog.Indexes[interval_idx].getSinceField()
                end_date_attr = catalog.Indexes[interval_idx].getUntilField()
                for brain in catalog({'meta_type': meta_type,
                                      interval_idx: date}):
                    path = brain.getPath()
                    if path in items:
                        continue
                    items[path] = None
                    event = brain.getObject()
                    if evalPredicate(predicate, event):
                        # TODO: refactor this callable thing with some code from TAL (PageTemplates)
                        start_date = getattr(event, start_date_attr)
                        if callable(start_date):
                            start_date = start_date()
                        end_date = getattr(event, end_date_attr)
                        if callable(end_date):
                            end_date = end_date()
                        events.append((event, self.getDate(start_date), self.getDate(end_date)))

        return events
    
    security.declareProtected(view, 'getDayEvents')
    def getDayEvents(self, date=''):
        """Return the events for the given day"""
        if date:
            try:
                return self.getEvents(date.year(), date.month(), date.day())
            except OverflowError:
                pass # bad date, return
        return []

    security.declareProtected(view, 'show_date')
    def show_date(self, date):
        try:
            return date.strftime('%d %B %Y')
        except:
            return ''

    # this is another implementation of the getEvents method; it's kept for reference
    #security.declareProtected(view, 'getEvents')
    #def getEvents(self, year, month, day=None):
    #    """Return the events for the specified date or the whole month if day
    #        is not specified.
    #    """
    #    if day:
    #        first_date = last_date = DateTime(year, month, day)
    #        # last_date = first_date.latestTime()
    #    else:
    #        first_date = DateTime(year, month, 1)
    #        last_date = DateTime(year, month, calendar.monthrange(year, month)[1]) #.latestTime()
    #
    #    events = []
    #    catalog = self.unrestrictedTraverse(self.catalog)
    #    items = {}
    #    for meta_type, (start_date_attr, end_date_attr,
    #                    predicate, interval_idx) in self.cal_meta_types.items():
    #        for query_kw in {start_date_attr: {'query': (first_date, last_date), \
    #                                           'range': 'minmax'}},              \
    #                        {end_date_attr:   {'query': (first_date, last_date), \
    #                                           'range': 'minmax'}},              \
    #                        {start_date_attr: {'query': first_date,              \
    #                                           'range': 'max'},                  \
    #                         end_date_attr:   {'query': last_date,               \
    #                                           'range': 'min'}}:
    #            for brain in catalog(meta_type=meta_type, **query_kw):
    #                path = brain.getPath()
    #                if path in items:
    #                    continue
    #                items[path] = None
    #                event = brain.getObject()
    #                if evalPredicate(predicate, event):
    #                    # TODO: refactor this callable thing with some code from TAL (PageTemplates)
    #                    start_date = getattr(event, start_date_attr)
    #                    if callable(start_date):
    #                        start_date = start_date()
    #                    end_date = getattr(event, end_date_attr)
    #                    if callable(end_date):
    #                        end_date = end_date()
    #                    events.append((event, self.getDate(start_date), self.getDate(end_date)))
    #    return events

    security.declareProtected(view, 'testCatalog')
    def testCatalog(self):
        """ test if catalog found """
        try:
            return bool(self.unrestrictedTraverse(self.catalog))
        except:
            return False

    #############################
    #   META TYPES FUNCTIONS    #
    #############################

    security.declareProtected(view_management_screens, 'testMetaType')
    def testMetaType(self, p_meta, p_property):
        """ test the meta types and asociated object properties """
        l_find = self.PrincipiaFind(self.getParent(), obj_metatypes=[p_meta], search_sub=1)
        if len(l_find)==0:
            return (0, 'No object found')
        if len(p_property)==0:
            return (0, 'Empty')
        if hasattr(l_find[0][1], p_property):
            return (1, 'Property found')
        return (0, 'No such property')

    security.declarePrivate('setCalMetaTypes')
    def setCalMetaTypes(self, p_meta_types):
        """ creates the dictionary for the cal_meta_types property """
        l_dict = {}
        l_list = self.utConvertLinesToList(p_meta_types)
        for item in l_list:
            if item in self.cal_meta_types:
                l_dict[item] = self.cal_meta_types[item]
            else:
                l_dict[item] = ('resource_interval', '')
        return l_dict


    ######################
    #   PROPERTIES TABS  #
    ######################

    security.declareProtected(view_management_screens, 'manageProperties')
    def manageProperties(self, title='', description='', day_len='',
                         cal_meta_types='', start_day='', catalog='',
                         REQUEST=None):
        """ manage basic properties """
        self.title =            title
        self.description =      description
        self.day_len =          day_len
        self.cal_meta_types =   self.setCalMetaTypes(cal_meta_types)
        self.start_day =        start_day
        self.catalog =          catalog
        self._p_changed = 1
        if REQUEST is not None:
            return REQUEST.RESPONSE.redirect('manage_properties')

    security.declareProtected(view_management_screens, 'manageStyleCalendar')
    def manageStyleCalendar(self, right_arrow='', left_arrow='', REQUEST=None):
        """ manage calendar css properties """
        for prop_name in self.css_calendar.keys():
            if self.REQUEST.has_key(prop_name):
                self.css_calendar[prop_name]=self.REQUEST[prop_name]

        img_ob = self._getOb('left_arrow')
        if left_arrow:
            if hasattr(left_arrow, 'filename'):
                l_read = left_arrow.read()
                if l_read != '':
                    img_ob.update_data(data=l_read)

        img_ob = self._getOb('right_arrow')
        if right_arrow:
            if hasattr(right_arrow, 'filename'):
                l_read = right_arrow.read()
                if l_read != '':
                    img_ob.update_data(data=l_read)

        self._p_changed = 1
        if REQUEST is not None:
            return REQUEST.RESPONSE.redirect('manage_style_calendar')

    security.declareProtected(view_management_screens, 'manageStyleEvents')
    def manageStyleEvents(self, REQUEST=None):
        """ manage events css properties """
        for prop_name in self.css_events.keys():
            if self.REQUEST.has_key(prop_name):
                self.css_events[prop_name]=self.REQUEST[prop_name]
        self._p_changed = 1
        if REQUEST is not None:
            return REQUEST.RESPONSE.redirect('manage_style_events')

    security.declareProtected(view_management_screens, 'manageMetaTypes')
    def manageMetaTypes(self, REQUEST=None):
        """ manage meta types properties """
        for meta in self.cal_meta_types:
            self.cal_meta_types[meta]=(self.REQUEST['idx_'+meta],
                                       self.REQUEST['app_'+meta])
        self._p_changed = 1
        if REQUEST is not None:
            return REQUEST.RESPONSE.redirect('manage_properties')


    #########################
    #   LAYOUT FUNCTIONS    #
    #########################

    security.declareProtected(view, 'getCSSProperty')
    def getCSSProperty(self, p_name):
        """ return a css property value for calendar"""
        if p_name in self.css_calendar.keys():
            return self.css_calendar[p_name]
        return ''

    security.declareProtected(view, 'getCSSTableBorder')
    def getCSSTableBorder(self):
        """ return values for table border """
        return self.getCSSProperty('border-weight') + 'px solid ' + self.getCSSProperty('border-color')

    security.declareProtected(view, 'getCSSDayBorder')
    def getCSSDayBorder(self):
        """ return values for day border """
        return self.getCSSProperty('day-border-weight') + 'px solid ' + self.getCSSProperty('day-border-color')

    security.declareProtected(view, 'getCSSEventBorder')
    def getCSSEventBorder(self):
        """ return values for day border """
        return self.getCSSProperty('event-border-weight') + 'px solid ' + self.getCSSProperty('event-border-color')

    security.declareProtected(view, 'getCSSTodayBorder')
    def getCSSTodayBorder(self):
        """ return values for day border """
        return self.getCSSProperty('today-border-weight') + 'px solid ' + self.getCSSProperty('today-border-color')

    security.declareProtected(view, 'getStyleEventProperty')
    def getStyleEventProperty(self, p_name):
        """ return a css property value for event """
        if p_name in self.css_events.keys():
            return self.css_events[p_name]
        return ''


    #####################
    #   MANAGEMENT TABS #
    #####################

    security.declarePublic('calendar_template')
    calendar_template = PageTemplateFile('zpt/calendar_template', globals())

    security.declareProtected(view_management_screens, 'manage_properties')
    manage_properties = PageTemplateFile('zpt/calendar_manage_properties', globals())

    security.declareProtected(view_management_screens, 'manage_style_calendar')
    manage_style_calendar = PageTemplateFile('zpt/calendar_manage_layout', globals())

    security.declareProtected(view_management_screens, 'manage_style_events')
    manage_style_events = PageTemplateFile('zpt/calendar_manage_events', globals())

    security.declarePublic('index_html')
    index_html = PageTemplateFile('zpt/calendar_month_events', globals())

    security.declarePublic('calendar_style_zmi_css')
    calendar_style_zmi_css = PageTemplateFile('zpt/calendar_style_zmi_css', globals())

    security.declarePublic('day_events')
    day_events = PageTemplateFile('zpt/calendar_day_events', globals())

    security.declarePublic('show_calendar')
    show_calendar = PageTemplateFile('zpt/calendar_index', globals())

InitializeClass(EventCalendar)
