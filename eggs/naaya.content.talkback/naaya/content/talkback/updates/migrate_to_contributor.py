# -*- coding: utf-8 -*-

from Products.naayaUpdater.updates import UpdateScript
from naaya.core.zope2util import physical_path

from naaya.content.talkback.comment_item import Contributor


class MigrateToContributor(UpdateScript):
    title = 'Migrate TalkBack comments to use Contributor instances.'
    authors = ['David Bătrânu']
    creation_date = 'Jan 22, 2019'

    def _update(self, portal):
        auth_tool = portal.getAuthenticationTool()
        query = {'meta_type': ['Naaya TalkBack Consultation']}
        for brain in portal.getCatalogTool()(**query):
            consultation = brain.getObject()

            count = 0
            for comment in all_comments(consultation):
                contributor_current = comment.contributor
                count_it = False

                # contributor_name is no longer used, data is computed
                # at runtime and exposed through get_contributor_info,
                # where the "display_name" key is equivalent to
                # "contributor_name".
                if hasattr(comment, 'contributor_name'):
                    try:
                        delattr(comment, 'contributor_name')
                        count_it = True
                    except AttributeError:
                        pass

                if not isinstance(contributor_current, Contributor):
                    source = ''
                    email = ''
                    organisation = ''
                    invite_key = ''

                    # Old style storage was: "invite:inviteKey" or
                    # "anonymous:User inputed name" or "userid".
                    if ':' in contributor_current:
                        source, value = contributor_current.split(':')
                    else:
                        value = contributor_current

                    if source == 'invite':
                        invite = comment.invitations.get_invitation(value)
                        name = invite.name
                        email = invite.email
                        invite_key = value

                    elif source == 'anonymous':
                        name = value

                    else:
                        name = value
                        user = auth_tool.get_user_with_userid(value)
                        if user:
                            email = auth_tool.getUserEmail(user)

                    comment.contributor = Contributor(
                        name=name,
                        email=email,
                        organisation=organisation,
                        source=source,
                        invite=invite_key,
                    )
                    count_it = True

                if count_it:
                    count += 1

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

