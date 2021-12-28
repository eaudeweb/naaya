''' customisations of the Naaya syndication '''
# pylint: disable=too-many-locals,dangerous-default-value


def application_expired(context, REQUEST=None, RESPONSE=None):
    """ Check if the etgg application survey is expired """
    survey = context.unrestrictedTraverse(
        '/demo-design/etgg2030/smecall/application_form')
    return survey.expired()
