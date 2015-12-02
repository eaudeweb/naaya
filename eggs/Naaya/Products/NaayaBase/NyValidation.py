"""
This module contains the class that handles the validation operation for a
single object.

The framework has a built in mechanism for validating content. Only the types
of objects for which their class extends the I{NyValidation} can be validated.
"""

from Globals import InitializeClass
from AccessControl import ClassSecurityInfo

class NyValidation:
    """
    Class that handles the validation operation for a single object.
    """

    security = ClassSecurityInfo()

    def __init__(self):
        """
        Initialize variables:

        B{validation_status} - integer value that stores validation status of
        the object:
            - B{-1} checked not OK
            - B{0} not checked
            - B{1} checked OK

        B{validation_date} - DateTime value that stores the date when the
        object was validated.

        B{validation_by} - string value that stores the id of the user that
        validated the object.

        B{validation_comment} - string value that stores additional comments

        B{contributor} - the id of the user that created the object

        B{approved_by} - the id of the user that approved the object
        """
        self.validation_status = 0
        self.validation_date = ''
        self.validation_by = ''
        self.validation_comment = ''
        self.contributor = ''
        self.approved_by = ''

    def checkThis(self, validation_status, validation_comment, validation_by,
                  validation_date=None):
        """
        Handles the validation operation.
        """

        if validation_date is None:
            validation_date = self.utGetTodayDate()
        elif validation_date == '' or validation_date =='2010/01/01':
            validation_date = ''
        else:
            validation_date = self.utGetDate(validation_date)
        self.validation_status = validation_status
        self.validation_date = validation_date
        self.validation_by = validation_by
        if validation_status == -1:
            self.validation_comment = validation_comment
        if validation_status in [0, 1] :
            self.validation_comment = ''
        self._p_changed = 1

InitializeClass(NyValidation)
