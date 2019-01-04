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
    """ """


def create_destinet_account_html(context, request):
    """ """
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
    """ """
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
        site.processRequestRoleForm(request)
        request.form[context.name_cookie] = request.form.get('username')
        request.form[context.pw_cookie] = request.form.get('password')
        request.SESSION.set(
            'title', '%s %s' %
            (request.form.get('firstname'), request.form.get('lastname')))
        transaction.commit()
        CookieCrumbler().modifyRequest(request, request.RESPONSE)
        redirect = request.RESPONSE.redirect(
            context.absolute_url() + '/login_html')
        if redirect != referer:
            # redirects to referer only when something is wrong in
            # the register form
            username = request.form['username']
            site.admin_addroles([username], ['Contributor'], '',
                                send_mail=True)
        else:
            # also call this to prefill values in form for contact
            prepare_error_response(context, register_schema,
                                   form_errors, request.form)
            # NOTE: disabled because the comments field is now optional
            # ugly hack as a conseq of renaming Comments field
            # if isinstance(request.SESSION.get('site_errors'), (tuple, list)):
            #     if 'Required field: Comments' in request.SESSION[
            #             'site_errors']:
            #         request.SESSION['site_errors'].remove(
            #             'Required field: Comments')
            #         request.SESSION['site_errors'].append(
            #             'Required field: About Me')
