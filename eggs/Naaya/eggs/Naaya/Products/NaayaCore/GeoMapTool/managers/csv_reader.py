import csv, codecs
import sys
from zLOG import LOG, ERROR

class UTF8Recoder:
    """
    Iterator that reads an encoded stream and reencodes the input to UTF-8
    """
    def __init__(self, f, encoding):
        self.reader = codecs.getreader(encoding)(f)

    def __iter__(self):
        return self

    def next(self):
        return self.reader.next().encode("utf-8")


class UnicodeReader:
    """
    A CSV reader which will iterate over lines in the CSV file "f",
    which is encoded in the given encoding.
    """

    def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
        f = UTF8Recoder(f, encoding)
        self.reader = csv.reader(f, dialect=dialect, **kwds)

    def next(self):
        row = self.reader.next()
        return [unicode(s, "utf-8") for s in row]

    def __iter__(self):
        return self

class CSVReader:
    """ Manipulate CSV files """

    def __init__(self, file, dialect, encoding):
        """ """
        if dialect == 'comma':
            dialect=csv.excel
        elif dialect == 'tab':
            dialect=csv.excel_tab
        else:
            dialect=csv.excel
        self.csv = UnicodeReader(file, dialect, encoding)

    def read(self):
        """ return the content of the file """
        try:
            header = self.csv.next()
            output = []
            while 1:
                buf = {}
                try:
                    values = self.csv.next()
                except StopIteration, error:
                    break
                else:
                    for field, value in zip(header, values):
                        buf[field.encode('utf-8')] = value.encode('utf-8')
                output.append(buf)
            return (output, '')
        except Exception, ex:
            err = sys.exc_info()
            LOG('NaayaCore.GeoMapTool.managers.CSVReader', ERROR, 'read error', error=err)
            return (None, ex)
