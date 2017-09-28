import LinkChecker
from App.ImageFile import ImageFile

def initialize(context):
    """ Initialize the LinkChecker product"""
    context.registerClass(
        LinkChecker.LinkChecker,
        constructors = (
        LinkChecker.manage_addLinkCheckerForm,
        LinkChecker.manage_addLinkChecker),
        icon = 'www/checker.gif'
      )

misc_ = {
  'logentry':ImageFile('www/logentry.gif', globals()),
}
