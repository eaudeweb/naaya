# The contents of this file are subject to the Mozilla Public
# License Version 1.1 (the "License"); you may not use this file
# except in compliance with the License. You may obtain a copy of
# the License at http://www.mozilla.org/MPL/
#
# Software distributed under the License is distributed on an "AS
# IS" basis, WITHOUT WARRANTY OF ANY KIND, either express or
# implied. See the License for the specific language governing
# rights and limitations under the License.
#
# The Initial Owner of the Original Code is European Environment
# Agency (EEA).  Portions created by Finsiel Romania and Eau de Web are
# Copyright (C) European Environment Agency.  All
# Rights Reserved.
#
# Authors:
#
# Alexandru Plugaru, Eau de Web
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo

from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Products.NaayaCore.NotificationTool.Subscriber import Subscriber
from Products.NaayaCore.NotificationTool.interfaces import ISubscriptionContainer

from Products.NaayaCore.managers.utils import is_valid_email

class AnonymousSubscriber(Subscriber):
    """ Overrides Subscriber behaviour to allow NotificationTool subscriptions for anonymous users"""
    
    security = ClassSecurityInfo()
    
    security.declarePublic('confirm')
    def confirm(self, REQUEST=None, key=''):
        """
        Verify a confirmation key for EmailNotifications and redirect to success page
        """
        if key:
            subscriptions_temp = self.getSite().portal_anonymous_notification.subscriptions_temp
            subscriptions = ISubscriptionContainer(self.getSite())
            for subscription in subscriptions_temp:# Check if the key (sha1) is in the temporary list
                if str(key) == subscription.key:
                    for existing_subscription in subscriptions:#Verify if the email is not already subscribed
                        if subscription.email == existing_subscription.email:
                            return REQUEST.RESPONSE.redirect(self.absolute_url() + '/confirm_error_exists')
                    subscriptions.add(subscription) # Add to subscribed list
                    del(subscriptions_temp[subscriptions_temp.index(subscription)]) # Remove from temporary list
                    return REQUEST.RESPONSE.redirect(self.absolute_url() + '/confirm_success')
            REQUEST.RESPONSE.setStatus(404); return self.confirm_error.pt_render()
        else:
            REQUEST.RESPONSE.setStatus(404); return self.confirm_error.pt_render()

    security.declarePublic('subscribe')
    def subscribe(self, REQUEST, notif_type, lang=None):
        """
        Add a new subscribtion. First to a temporary list,
        then after confirmation to the correct container
        """
        email  = REQUEST.get('email', '')
        organisation = REQUEST.get('organisation', '')
        sector = REQUEST.get('sector', '')
        country = REQUEST.get('country', '')
        errors = {} 
        REQUEST.SESSION['errors'] = {}
         # Send errors back to form
        if not is_valid_email(email):
            errors['email'] = True
        if not organisation:
            errors['organisation'] = True
        if not lang:
            lang = self.get_implicit_lang()
        try:
            notificationTool = self.getSite().portal_anonymous_notification
            notificationTool.add_email_subscription(
                email,
                organisation,
                sector,
                country,
                notif_type,
                lang,
                str(self.absolute_url()) + '/confirm'
            )
        except ValueError, e:
            if is_valid_email(email):
                errors['email_exists'] = True
        
        if not len(errors):
            return REQUEST.RESPONSE.redirect(self.absolute_url() + '/thank_you')
        else:
            REQUEST.SESSION['errors'] = errors
            return REQUEST.RESPONSE.redirect(self.absolute_url())
            
    security.declarePublic('delete_subscription')
    def delete_subscription(self, REQUEST, email, location='', notif_type='', lang=''):
        """ User doesn't want to receive notifications any more """
        notificationTool = self.getSite().portal_anonymous_notification
        try:
            notificationTool.remove_account_subscription(email, location, notif_type, lang)
            return REQUEST.RESPONSE.redirect(self.absolute_url() + '/delete_success')
        except ValueError:
            return REQUEST.RESPONSE.setStatus(404); return self.delete_error.pt_render()
            
    security.declarePublic('get_enabled_subscriptions')
    def get_enabled_subscriptions(self, REQUEST):
        return list(self.list_enabled_subscriptions())
        
    index_html = PageTemplateFile('zpt/subscribe', globals())# Subscribe form
    thank_you = PageTemplateFile('zpt/thank_you', globals()) #This is the thank you page after the user submitted the form
    confirm_success = PageTemplateFile('zpt/confirm_success', globals())
    confirm_error = PageTemplateFile('zpt/confirm_error', globals())
    confirm_error_exists = PageTemplateFile('zpt/confirm_error_exists', globals()) # this email exists
    delete_success = PageTemplateFile('zpt/delete_success', globals()) #Subscribtion deleted
    delete_error = PageTemplateFile('zpt/delete_error', globals())

InitializeClass(AnonymousSubscriber)