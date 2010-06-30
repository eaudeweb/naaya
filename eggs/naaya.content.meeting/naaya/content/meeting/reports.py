#Python imports
try:
    import json
except ImportError:
    import simplejson as json

#Zope imports
from OFS.SimpleItem import SimpleItem
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import view

#Naaya imports
from Products.NaayaCore.FormsTool.NaayaTemplate import NaayaPageTemplateFile

#naaya.content.meeting improts
import meeting as meeting_module
from utils import getUserFullName, getUserEmail, getUserOrganisation

class MeetingReports(SimpleItem):
    """ """
    security = ClassSecurityInfo()

    title = "Meeting Reports"
    participant_icon = 'images/report_icons/participant.gif'
    organisation_icon = 'images/report_icons/organisation.gif'

    def __init__(self, id):
        """ """
        self.id = id

    def jstree_participants(self):
        """ """
        jstree, participants = [], {}
        site = self.getSite()
        meeting_config = meeting_module.get_config()
        meeting_obs = site.getCatalogedObjectsCheckView(meta_type=meeting_config['meta_type'], approved=1)

        for meeting_ob in meeting_obs:
            for uid in meeting_ob.participants.uids:
                if uid not in participants:
                    participants[uid] = []
                participants[uid].append(meeting_ob)

        for uid, meetings_part in participants.iteritems():
            meeting_nodes = []
            for meeting_ob in meetings_part:
                title = meeting_ob.title_or_id()
                icon = meeting_ob.icon
                href = meeting_ob.absolute_url()
                meeting_nodes.append({'data':
                                            {'title': title,
                                             'icon': icon,
                                             'attributes':
                                                     {'href': href}
                                    }})

            name = getUserFullName(site, uid)
            icon = self.participant_icon
            user_node = {'data':
                                {'title': name,
                                 'icon': icon,
                                 'attributes':
                                    {'href': ''}
                                },
                            'children': meeting_nodes}
            email = getUserEmail(site, uid)
            if email is not None:
                href = 'mailto:' + email
                user_node['data']['attributes'] = {'href': href}
            jstree.append(user_node)

        return json.dumps(jstree)

    def jstree_organisations(self):
        """ """
        jstree, organisations = [], {}
        site = self.getSite()
        meeting_config = meeting_module.get_config()
        meeting_obs = site.getCatalogedObjectsCheckView(meta_type=meeting_config['meta_type'], approved=1)

        for i, meeting in enumerate(meeting_obs):
            for uid in meeting.participants.uids:
                organisation = getUserOrganisation(site, uid)
                if organisation not in organisations:
                    organisations[organisation] = {}
                if i not in organisations[organisation]:
                    organisations[organisation][i] = []
                organisations[organisation][i].append(uid)

        for organisation, values in organisations.iteritems():
            meeting_nodes = []
            for i, uids in values.iteritems():
                meeting = meeting_obs[i]

                user_nodes = []
                for uid in uids:
                    name = getUserFullName(site, uid)
                    user_node = {'data':
                                        {'title': name,
                                        'icon': self.participant_icon,
                                        'attributes':
                                            {'href': ''}
                                        }}
                    email = getUserEmail(site, uid)
                    if email is not None:
                        href = 'mailto:' + email
                        user_node['data']['attributes']['href'] = href
                    user_nodes.append(user_node)

                title = meeting.title_or_id()
                href = meeting.absolute_url()
                meeting_nodes.append({'data':
                                        {'title': title,
                                        'icon': meeting.icon,
                                        'attributes':
                                            {'href': href}},
                                    'children': user_nodes})


            jstree.append({'data':
                                {'title': organisation,
                                'icon': self.organisation_icon
                            },
                            'children': meeting_nodes
                        })
        return json.dumps(jstree)
 
    security.declareProtected(view, 'report_meeting_participants')
    def report_meeting_participants(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'report_meeting_participants')

    security.declareProtected(view, 'report_meeting_organisations')
    def report_meeting_organisations(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'report_meeting_organisations')

#Custom page templates
NaayaPageTemplateFile('zpt/report_meeting_participants', globals(), 'report_meeting_participants')
NaayaPageTemplateFile('zpt/report_meeting_organisations', globals(), 'report_meeting_organisations')

