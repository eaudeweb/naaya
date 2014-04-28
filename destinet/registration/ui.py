""" User interface methods (views) regarding registration in Destinet """

from Products.NaayaBase.NyContentType import SchemaFormHelper
from destinet.registration.constants import EW_REGISTER_FIELD_NAMES
from destinet.registration.constants import WIDGET_NAMES
from destinet.registration.core import prepare_error_response, handle_groups
from destinet.registration.core import validate_widgets
from naaya.content.contact.contact_item import _create_NyContact_object


def render_create_account_tpl(context, widgets, request_form=None, errors=None):
    """ """


def create_destinet_account_html(context, request):
    """ """
    schema_tool = context.getSite().getSchemaTool()

    contact_schema = schema_tool['NyContact']
    register_extra_schema = schema_tool['registration']

    contact_helper = SchemaFormHelper(contact_schema, context)
    register_helper = SchemaFormHelper(register_extra_schema, context)

    widgets = {}
    for name in WIDGET_NAMES:
        widgets[name] = contact_helper._get_renderer(
            name, contact_schema["%s-property" % name], False)

    groups_widget = register_helper._get_renderer(
        'groups', register_extra_schema['groups-property'], False)

    ns = {'widgets': widgets,
          'here': context,
          'groups_widget': groups_widget}

    return context.getFormsTool().getContent(ns, 'site_createaccount')


def process_create_account(context, request):
    """ """
    referer = request.HTTP_REFERER
    site = context.getSite()
    schema = site.getSchemaTool()['NyContact']
    register_schema = context.getSite().getSchemaTool()['registration']
    form_data, form_errors = validate_widgets(schema, register_schema, request.form)

    # if filling up the lower part, then the upper part is required as well
    if form_data['landscape_type'] and not form_data['topics']:
        form_errors['topics'] = ['Value is required for Topics']

    if form_errors:
        prepare_error_response(context, schema, register_schema, form_errors, request.form)
        # we need to put ourselves the user specific values in form
        args_for_session = {}
        for key in EW_REGISTER_FIELD_NAMES:
            args_for_session[key] = request.form.get(key)
        args_for_session['name'] = request.form.get('username')
        site.setRequestRoleSession(**args_for_session)
        request.RESPONSE.redirect(referer)
    else:
        # OBS: email is already sent here:
        real_comment = request.form.get('comments')
        if not real_comment:
            request.form['comments'] = " "
        site.processRequestRoleForm(request)
        redirect = request.RESPONSE.headers.get('location')
        if redirect != referer:
            # redirects to referer only when something is wrong in register form
            where = site['who-who']['destinet-users']
            username = request.form['username']
            contact_name = "%(firstname)s %(lastname)s" % request.form
            ob = _create_NyContact_object(where, username, username)
            ob.releasedate = site.utGetTodayDate()
            ob.approveThis(1, username)
            ob.submitThis()
            ob.giveEditRights()
            # voodoo for setting ownership using AccessControl.Owned API
            new_user = site.acl_users.getUser(username).__of__(site.acl_users)
            ob.changeOwnership(new_user)

            site.admin_addroles([username], ['Contributor'], '', send_mail=True)

            # hack to edit object without permissions (no auth)
            setattr(ob, 'checkPermissionEditObject', lambda: True)
            ob.manageProperties(title=contact_name,
                                firstname=request.form['firstname'],
                                lastname=request.form['lastname'],
                                organisation=request.form['organisation'],
                                approved=True,
                                description=real_comment,
                                **form_data)
            handle_groups(ob, request.form)
            delattr(ob, 'checkPermissionEditObject')
        else:
            # also call this to prefill values in form for contact
            prepare_error_response(context, schema, register_schema, form_errors, request.form)
            # NOTE: disabled because the comments field is now optional
            # ugly hack as a conseq of renaming Comments field
            # if isinstance(request.SESSION.get('site_errors'), (tuple, list)):
            #     if 'Required field: Comments' in request.SESSION['site_errors']:
            #         request.SESSION['site_errors'].remove('Required field: Comments')
            #         request.SESSION['site_errors'].append('Required field: About Me')
