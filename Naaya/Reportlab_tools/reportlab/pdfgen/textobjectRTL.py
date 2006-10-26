import string
from types import *
from reportlab.lib import colors
from reportlab.lib.colors import ColorType
from reportlab.lib.utils import fp_str
from reportlab.pdfbase import pdfmetrics

import textobject
try:
    import pyfribidi    #linux
except ImportError:
    import _pyfribidi as pyfribidi  #win

try:
    from pyfribidi import RTL   #linux
except ImportError:
    RTL = 1 #win

_SeqTypes=(TupleType,ListType)


class PDFTextObjectRTL(textobject.PDFTextObject):

    def isRTL(self):
        return 1

    def emitTextOrigin(self, x, y):
        if self._canvas.bottomup:
            self._code.append('1 0 0 1 %s Tm' % fp_str(x, y)) #bottom up
        else:
            self._code.append('1 0 0 -1 %s Tm' % fp_str(x, y))  #top down

    def _formatText(self, text):
        "Generates PDF text output operator(s)"
        text = pyfribidi.log2vis(text, RTL)
        if self._dynamicFont:
            results = []
            font = pdfmetrics.getFont(self._fontname)
            for subset, chunk in font.splitString(text, self._canvas._doc):
                if subset != self._curSubset:
                    pdffontname = font.getSubsetInternalName(subset, self._canvas._doc)
                    results.append("%s %s Tf %s TL" % (pdffontname, fp_str(self._fontsize), fp_str(self._leading)))
                    self._curSubset = subset
                chunk = self._canvas._escape(chunk)
                results.append("(%s) Tj" % chunk)
            return string.join(results, ' ')
        else:
            text = self._canvas._escape(text)
            return "(%s) Tj" % text

    def _textOut(self, text, TStar=0):
        "prints string at current point, ignores text cursor"
        self._code.append('%s%s' % (self._formatText(text), (TStar and ' T*' or '')))

    def textOut(self, text):
        """prints string at current point, text cursor moves across."""
        self._x = self._x - self._canvas.stringWidth(text, self._fontname, self._fontsize)
        self.emitTextOrigin(self._x, self._y)
        self._code.append(self._formatText(text))

    def textLine(self, text=''):
        """prints string at current point, text cursor moves down.
        Can work with no argument to simply move the cursor down."""
        self._x = self._x0
        if self._canvas.bottomup:
            self._y = self._y - self._leading
        else:
            self._y = self._y + self._leading
        left_x = self._x - self._canvas.stringWidth(text, self._fontname, self._fontsize)
        self.emitTextOrigin(left_x, self._y)
        self._code.append('%s T*' % self._formatText(text))

    def textLines(self, stuff, trim=1):
        """prints multi-line or newlined strings, moving down.  One
        comon use is to quote a multi-line block in your Python code;
        since this may be indented, by default it trims whitespace
        off each line and from the beginning; set trim=0 to preserve
        whitespace."""
        if type(stuff) == StringType:
            lines = string.split(string.strip(stuff), '\n')
            if trim==1:
                lines = map(string.strip,lines)
        elif type(stuff) == ListType:
            lines = stuff
        elif type(stuff) == TupleType:
            lines = stuff
        else:
            assert 1==0, "argument to textlines must be string,, list or tuple"

        for line in lines:
            left_x = self._x - self._canvas.stringWidth(text, self._fontname, self._fontsize)
            self.emitTextOrigin(left_x, self._y)
            self._code.append('%s T*' % self._formatText(line))
            if self._canvas.bottomup:
                self._y = self._y - self._leading
            else:
                self._y = self._y + self._leading
        self._x = self._x0

    def __nonzero__(self):
        'PDFTextObject is true if it has something done after the init'
        return self._code != ['BT']
