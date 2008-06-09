"""
contains DOM Style Sheets MediaList implementation class.

TODO:
    implement readonly
    delete: maybe if deleting from all, exchange all for all others?
"""
__version__ = '0.51'

import xml.dom


class MediaList(list):
    """
    provides the abstraction of an ordered collection of media,
    without defining or constraining how this collection is
    implemented. An empty list is the same as a list that
    contains the medium "all".
    """
    
    _MEDIA = [u'all', u'braille', u'embossed', u'handheld ', u'print',
                    u'projection ', u'screen', u'speech', u'tty', u'tv']

    _readonly = False

    # fget    
    def _getLength(self):
        return len(self)
    # property
    length = property(_getLength,
                      doc="(DOM attribute) The number of media\
                      in the list.")

    # fget
    def getFormatted(self):
        if len(self) == 0:
            return u'all'
        else:
            return u', '.join(self)
    # fset
    def _setMediaText(self, mediaText):
        if self._readonly:
            raise xml.dom.NoModificationAllowedErr()
        del self[:]
        for m in mediaText.split(u','):
            try:
                self.appendMedium(m)
            except xml.dom.InvalidCharacterErr:
                raise xml.dom.SyntaxErr(u'"%s" is not a valid medium' % m)
    # property
    mediaText = property(getFormatted, _setMediaText,
                         doc="(DOM attribute) The parsable textual\
                         representation of the media list.\
                         This is a comma-separated list of media.")    
    
    def appendMedium(self, medium):
        """
        (DOM method) Adds the medium to the end of the list.
        If the medium is already used, it is first removed.
        """
        if self._readonly:
            raise xml.dom.NoModificationAllowedErr()
        medium = medium.strip()
        # If the medium contains characters that are invalid in the 
        # underlying style language. ???
        if medium not in self._MEDIA:
            raise xml.dom.InvalidCharacterErr(
                u'"%s" is not a valid medium' % medium)
        # all contains it!
        if self == [u'all']:
            return
        if medium == u'all':
            del self[:]
            self.append(u'all')
            return
        else:
            if medium in self:
                self.remove(medium)
            self.append(medium)
    
    def deleteMedium(self, medium):
        """
        (DOM method) @param medium to delete in the media list.
        """
        if self._readonly:
            raise xml.dom.NoModificationAllowedErr()
        try:
            self.remove(medium)
        except ValueError:
            raise xml.dom.NotFoundErr(
                u'"%s" not in this MediaList' % medium)

    def item(self, index):
        """
        (DOM method) Returns the indexth in the list.
        If index is greater than or equal to the number
        of media in the list, this returns null (None).
        """
        try:
            return self[index]
        except IndexError:
            return None

