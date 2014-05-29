from datetime import datetime

from AccessControl import ClassSecurityInfo
from Globals import InitializeClass

class Interval(tuple):
    """ Immutable type representing two datetime intervals and all_day option

    """

    security = ClassSecurityInfo()

    def __new__(cls, start_date=None, end_date=None, all_day=False):
        if start_date is not None and start_date > end_date:
            raise ValueError('End time can not precede start time')
        if all_day:
            # strip h:m since they are all_day
            # could use start_date.date(), but we prefer to maintain data type
            start_date = datetime(start_date.year, start_date.month, start_date.day)
            end_date = datetime(end_date.year, end_date.month, end_date.day)
        return tuple.__new__(cls, (start_date, end_date, all_day))


    security.declarePublic('start_date')
    @property
    def start_date(self):
        return self[0]

    security.declarePublic('end_date')
    @property
    def end_date(self):
        return self[1]

    security.declarePublic('all_day')
    @property
    def all_day(self):
        return self[2]

    def __repr__(self):
        if self == Interval():
            return "empty Interval()"
        data = {
            'start_date': self.start_date.strftime("%d/%m/%Y"),
            'end_date': self.end_date.strftime("%d/%m/%Y"),
            'start_time': self.start_date.strftime("%H:%M"),
            'end_time': self.end_date.strftime("%H:%M"),
            'all_day': repr(self.all_day),
        }
        return ("Interval:[%(start_date)s, %(start_time)s - "
                "%(end_date)s, %(end_time)s; All day: %(all_day)s]"
                % data)

InitializeClass(Interval)
