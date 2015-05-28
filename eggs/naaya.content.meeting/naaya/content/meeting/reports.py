# Python imports
try:
    import simplejson as json
except ImportError:
    import json

# Zope imports
from OFS.SimpleItem import SimpleItem
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import view

# Naaya imports
from Products.NaayaCore.FormsTool.NaayaTemplate import NaayaPageTemplateFile

# naaya.content.meeting imports
import meeting as meeting_module
from utils import getUserFullName, getUserEmail, getUserOrganization


class MeetingReports(SimpleItem):
    """ """
    security = ClassSecurityInfo()

    title = "Meeting Reports"
    participant_icon = 'misc_/NaayaContent/participant.gif'
    organization_icon = 'misc_/NaayaContent/organization.gif'

    def __init__(self, id):
        """ """
        self.id = id

    def jstree_participants(self):
        """ """
        jstree, participants = [], {}
        site = self.getSite()
        meeting_config = meeting_module.get_config()
        meeting_obs = site.getCatalogedObjectsCheckView(
            meta_type=meeting_config['meta_type'], approved=1)

        for meeting_ob in meeting_obs:
            for uid in meeting_ob.participants.get_participants():
                if uid not in participants:
                    participants[uid] = []
                participants[uid].append(meeting_ob)

        for uid, meetings_part in participants.iteritems():
            meeting_nodes = []
            for meeting_ob in meetings_part:
                title = meeting_ob.title_or_id()
                icon = meeting_ob.icon
                href = meeting_ob.absolute_url()
                meeting_nodes.append({'data': {'title': title,
                                               'icon': icon,
                                               'attributes': {'href': href}
                                               }})

            name = getUserFullName(site, uid)
            icon = self.participant_icon
            user_node = {'data': {'title': name,
                                  'icon': icon,
                                  'attributes': {'href': ''}
                                  },
                         'children': meeting_nodes}
            email = getUserEmail(site, uid)
            if email is not None:
                href = 'mailto:' + email
                user_node['data']['attributes'] = {'href': href}
            jstree.append(user_node)

        return json.dumps(jstree)

    def jstree_organizations(self):
        """ """
        jstree, organizations = [], {}
        site = self.getSite()
        meeting_config = meeting_module.get_config()
        meeting_obs = site.getCatalogedObjectsCheckView(
            meta_type=meeting_config['meta_type'], approved=1)

        for i, meeting in enumerate(meeting_obs):
            for uid in meeting.participants.get_participants():
                organization = getUserOrganization(site, uid)
                if organization not in organizations:
                    organizations[organization] = {}
                if i not in organizations[organization]:
                    organizations[organization][i] = []
                organizations[organization][i].append(uid)

        for organization, values in organizations.iteritems():
            meeting_nodes = []
            for i, uids in values.iteritems():
                meeting = meeting_obs[i]

                user_nodes = []
                for uid in uids:
                    name = getUserFullName(site, uid)
                    user_node = {'data': {'title': name,
                                          'icon': self.participant_icon,
                                          'attributes': {'href': ''}
                                          }}
                    email = getUserEmail(site, uid)
                    if email is not None:
                        href = 'mailto:' + email
                        user_node['data']['attributes']['href'] = href
                    user_nodes.append(user_node)

                title = meeting.title_or_id()
                href = meeting.absolute_url()
                meeting_nodes.append({'data': {'title': title,
                                               'icon': meeting.icon,
                                               'attributes': {'href': href}},
                                      'children': user_nodes})

            jstree.append({'data': {'title': organization,
                                    'icon': self.organization_icon},
                           'children': meeting_nodes
                           })
        return json.dumps(jstree)

    security.declareProtected(view, 'report_meeting_participants')

    def report_meeting_participants(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self},
                                              'report_meeting_participants')

    security.declareProtected(view, 'report_meeting_organizations')

    def report_meeting_organizations(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self},
                                              'report_meeting_organizations')

# Custom page templates
NaayaPageTemplateFile('zpt/report_meeting_participants', globals(),
                      'report_meeting_participants')
NaayaPageTemplateFile('zpt/report_meeting_organizations', globals(),
                      'report_meeting_organizations')
