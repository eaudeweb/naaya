import calendar
from time import localtime
from datetime import datetime, date

#Can we lose this please?
from DateTime import DateTime

class DateFunctions(object):
    """ date functions """

    #################
    #   CONSTANTS   #
    #################

    LongWeekdays = {"0":"Monday",
                    "1":"Tuesday",
                    "2":"Wednesday",
                    "3":"Thursday",
                    "4":"Friday",
                    "5":"Saturday",
                    "6":"Sunday"}
    day_name_length =['1', '2', '3', 'All']
    mdays = [0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]


    ###############
    #   GETTERS   #
    ###############

    def getCurrentYear(self):
        """ return current year """
        return localtime()[0]

    def getCurrentMonth(self):
        """ return current month """
        return localtime()[1]

    def getCurrentDay(self):
        """ return current day """
        return localtime()[2]

    def getShortWeekdays(self, p_length):
        """."""
        return self.utGenerateList(self.getDayIndex(self.start_day), self.utDayLength(p_length))

    def LongMonths(self, p_index):
        """ return the month's name """
        setTranslation = self.getSite().getPortalI18n().get_translation
        if p_index == 0:
            return setTranslation('January')
        elif p_index == 1:
            return setTranslation('February')
        elif p_index == 2:
            return setTranslation('March')
        elif p_index == 3:
            return setTranslation('April')
        elif p_index == 4:
            return setTranslation('May')
        elif p_index == 5:
            return setTranslation('June')
        elif p_index == 6:
            return setTranslation('July')
        elif p_index == 7:
            return setTranslation('August')
        elif p_index == 8:
            return setTranslation('September')
        elif p_index == 9:
            return setTranslation('October')
        elif p_index == 10:
            return setTranslation('November')
        elif p_index == 11:
            return setTranslation('December')

    def LongDays(self, p_index):
        """ return the day's name """
        setTranslation = self.getSite().getPortalI18n().get_translation
        if p_index == 0:
            return setTranslation('Monday')
        elif p_index == 1:
            return setTranslation('Tuesday')
        elif p_index == 2:
            return setTranslation('Wednesday')
        elif p_index == 3:
            return setTranslation('Thursday')
        elif p_index == 4:
            return setTranslation('Friday')
        elif p_index == 5:
            return setTranslation('Saturday')
        elif p_index == 6:
            return setTranslation('Sunday')

    def getLongWeekdays(self):
        """ return long weekdays """
        l_LongWeekdays={}
        for i in range(7):
            l_LongWeekdays[str(i)]=self.LongDays(i)
        return l_LongWeekdays

    def getLongWeekdaysSorted(self):
        """ return long day's name sorted """
        return self.sortedDictByKey(self.getLongWeekdays())

    def getDayIndex(self, p_day):
        """ return the day index """
        for key in self.LongWeekdays.keys():
            if self.LongWeekdays[key] == p_day:  return int(key)
#the code bellow will not work if week days will be translated:
#        for key in self.getLongWeekdays().keys():
#            if self.getLongWeekdays()[key] == p_day:  return int(key)

    def getDayLengths(self):
        """ return the choises for day length """
        l_length = []
        l_length.extend(self.day_name_length)
        return l_length

    #################
    #   FUNCTIONS   #
    #################

    def isCurrentDay(self, p_day, p_month, p_year):
        """ test if current day """
        return self.getCurrentDay() == p_day and \
               self.getCurrentMonth() == int(p_month) and \
               int(self.getCurrentYear()) == int(p_year)

    def getNextDate(self, p_month, p_year):
        """ return next month """
        if int(p_month) < 12:
            return (int(p_month)+1, int(p_year))
        else:
            return (1, int(p_year)+1)

    def getPrevDate(self, p_month, p_year):
        """ return last month """
        if int(p_month) > 1:
            return (int(p_month)-1, int(p_year))
        else:
            return (12, int(p_year)-1)

    def getMonthName(self, p_month):
        """ reurns the month's name """
        return self.LongMonths(int(p_month)-1)

    def getYear(self, p_date):
        """ return year from a given date """
        l_date = str(p_date)
        if l_date != '':
            try:    return str(DateTime(l_date).year())
            except: return ''
        else:       return ''

    def getMonth(self, p_date):
        """ return month from a given date """
        l_date = str(p_date)
        if l_date != '':
            try:    return str(DateTime(l_date).month())
            except: return ''
        else:       return ''

    def getDay(self, p_date):
        """ return day from a given date """
        l_date = str(p_date)
        if l_date != '':
            try:    return str(DateTime(l_date).day())
            except: return ''
        else:       return ''

    def getDate(self, p_date):
        """ return date """
        setTranslation = self.getSite().getPortalI18n().get_translation
        l_date = str(p_date)
        if l_date != '':
            try:    return DateTime(l_date).strftime("%d %B %Y")
            except: return setTranslation('empty')
        else:       return setTranslation('empty')

    def getDateFromMinutes(self, minutes):
        """ return date based on minutes coresponding to an indexed date """
        try:
            return datetime.fromtimestamp(minutes * 60)
        except:
            return None

    def getMonthRange(self, year, month):
        """ return weekday (0-6 ~ Mon-Sun) and number of days (28-31)
        for year, month """
        start_day, end_day = calendar.monthrange(year, month)
        return date(year, month, 1).weekday(), end_day

