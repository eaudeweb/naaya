from Products.naayaUpdater.updates import UpdateScript
from naaya.core.zope2util import physical_path

class SetUserInfo(UpdateScript):
    title = 'Set user info on TalkBack comments'
    authors = ['Alex Morega']
    creation_date = 'Oct 19, 2010'

    def _update(self, portal):
        query = {'meta_type': ['Naaya TalkBack Consultation']}
        for brain in portal.getCatalogTool()(**query):
            consultation = brain.getObject()

            count = 0
            for comment in all_comments(consultation):
                if comment.contributor_name is None:
                    try:
                        comment._save_contributor_name()
                        count += 1
                    except AttributeError:
                        # _save_contributor_name no longer exists,
                        # contributor data is retrieved at runtime through
                        # get_contributor_info
                        continue

            consultation_path = physical_path(consultation)
            if count > 0:
                self.log.info("%r: %d comments", consultation_path, count)
            else:
                self.log.info("%r: nothing to update", consultation_path)

        return True


def all_comments(consultation):
    for section in consultation.list_sections():
        for paragraph in section.get_paragraphs():
            for comment in paragraph.get_comments():
                yield comment

