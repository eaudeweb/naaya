""" User interface methods (views) regarding registration in Destinet """

import transaction
from zExceptions import BadRequest

from Products.NaayaCore.AuthenticationTool.CookieCrumbler import CookieCrumbler
from Products.NaayaCore.AuthenticationTool.AuthenticationTool import \
    check_username
from Products.NaayaBase.NyContentType import SchemaFormHelper
from destinet.registration.constants import EW_REGISTER_FIELD_NAMES
from destinet.registration.constants import WIDGET_NAMES
from destinet.registration.core import prepare_error_response
from destinet.registration.core import validate_widgets
from naaya.core.utils import is_valid_email


def render_create_account_tpl(context, widgets, request_form=None,
                              errors=None):
    """ Render create account tpl """


def create_destinet_account_html(context, request):
    """ Create destinet account html """
    schema_tool = context.getSite().getSchemaTool()

    contact_schema = schema_tool['NyContact']

    contact_helper = SchemaFormHelper(contact_schema, context)

    widgets = {}
    for name in WIDGET_NAMES:
        widgets[name] = contact_helper._get_renderer(
            name, contact_schema["%s-property" % name], False)

    ns = {'widgets': widgets,
          'here': context}

    return context.getFormsTool().getContent(ns, 'site_createaccount')


def process_create_account(context, request):
    """ Process create account """
    if request.form == {}:
        raise BadRequest('Empty request form')
    referer = request.HTTP_REFERER
    site = context.getSite()
    register_schema = context.getSite().getSchemaTool()['registration']
    form_data, form_errors = validate_widgets(register_schema, request.form)
    email = request.form.get('email')
    if not (email and is_valid_email(email)):
        form_errors['email'] = ['Invalid email address']
    username = request.form.get('username')
    if not (check_username(username)):
        form_errors['username'] = [
            'Username: only letters and numbers allowed']
    if request.form.get('password') != request.form.get('confirm'):
        form_errors['password'] = ["Password doesn't match verification"]
    if form_errors:
        prepare_error_response(context, register_schema, form_errors,
                               request.form)
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
        form = request.form
        username = form.get('username', '')
        auth_tool = site.getAuthenticationTool()
        existed = auth_tool.getUser(username) is not None
        site.processRequestRoleForm(
            username=username,
            password=form.get('password', ''),
            confirm=form.get('confirm', ''),
            firstname=form.get('firstname', ''),
            lastname=form.get('lastname', ''),
            email=form.get('email', ''),
            organisation=form.get('organisation', ''),
            location=form.get('location', ''),
            comments=form.get('comments', ''),
            REQUEST=request)
        if existed or auth_tool.getUser(username) is None:
            # not created: processRequestRoleForm set the error; back to the form
            prepare_error_response(context, register_schema,
                                   form_errors, request.form)
            request.RESPONSE.redirect(referer)
            return
        request.form[context.name_cookie] = username
        request.form[context.pw_cookie] = request.form.get('password')
        request.SESSION.set(
            'title', '%s %s' %
            (request.form.get('firstname'), request.form.get('lastname')))
        transaction.commit()
        CookieCrumbler().modifyRequest(request, request.RESPONSE)
        came_from = request.SESSION.get('came_from')
        if came_from:
            request.RESPONSE.redirect(came_from)
        else:
            request.RESPONSE.redirect(context.absolute_url() + '/login_html')
        site.admin_addroles([username], ['Contributor'], '', send_mail=True)
