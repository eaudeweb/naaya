""" User interface methods (views) regarding registration in Destinet """
from Products.NaayaBase.NyContentType import SchemaFormHelper
from naaya.content.contact.contact_item import _create_NyContact_object

from destinet.registration.core import validate_widgets, prepare_error_response
from destinet.registration.constants import WIDGET_NAMES


def render_create_account_tpl(context, widgets, request_form=None, errors=None):
    """ """

def create_destinet_account_html(context, request):
    """ """
    ns = {'here': context}
    schema = context.getSite().getSchemaTool()['NyContact']
    sh = SchemaFormHelper(schema, context)
    widgets = []
    for wid in WIDGET_NAMES:
        widgets.append(sh._get_renderer(wid, schema["%s-property" % wid], False))
    ns = {'widgets': widgets,
          'here': context}
    return context.getFormsTool().getContent(ns, 'site_createaccount')

def process_create_account(context, request):
    """ """
    referer = request.HTTP_REFERER
    site = context.getSite()
    schema = site.getSchemaTool()['NyContact']
    form_data, form_errors = validate_widgets(schema, request.form)
    if form_errors:
        prepare_error_response(context, schema, form_errors, request.form)
        # we need to put ourselves the user specific values in form
        args_for_session = {}
        for key in EW_REGISTER_FIELD_NAMES:
            args_for_session[key] = request.form.get(key)
        args_for_session['name'] = request.form.get('username')
        site.setRequestRoleSession(**args_for_session)
        request.RESPONSE.redirect(referer)
    else:
        # OBS: email is already sent here:
        site.processRequestRoleForm(request)
        redirect = request.RESPONSE.headers.get('location')
        if redirect != referer:
            # redirects to referer only when something is wrong in register form
            where = site['who-who']['destinet-users']
            username = request.form['username']
            contact_name = "%(firstname)s %(lastname)s" % request.form
            ob = _create_NyContact_object(where, username, username)
            ob.approveThis(0, None)
            ob.submitThis()
            ob.giveEditRights()
            # voodoo for setting ownership using AccessControl.Owned API
            new_user = site.acl_users.getUser(username).__of__(site.acl_users)
            ob.changeOwnership(new_user)
            # hack to edit object without permissions (no auth)
            setattr(ob, 'checkPermissionEditObject', lambda: True)
            ob.manageProperties(title=contact_name,
                                firstname=request.form['firstname'],
                                lastname=request.form['lastname'],
                                organisation=request.form['organisation'],
                                **form_data)
            delattr(ob, 'checkPermissionEditObject')
        else:
            # also call this to prefill values in form for contact
            prepare_error_response(context, schema, form_errors, request.form)
