from zope2util import json_response


def frame_view(context, request):
    # TODO unit tests
    # TODO documentation
    user = request.AUTHENTICATED_USER
    site = context.getSite()
    users_tool = site.acl_users
    first_name = ''
    last_name = ''
    email = ''
    phone_number = ''
    try:
        if hasattr(site, "member_search"):
            user_ob = site.member_search._search_users(user.getId())[0]
        else:
            user_ob = users_tool.search_users(user.getId(), all_users=True)[0]
        first_name = user_ob.first_name
        last_name = user_ob.last_name
        phone_number = user_ob.phone_number
        email = user_ob.email
    except:
        pass
    response_data = {
        'frame_html': context['frame.html'](),
        'user_id': user.getId(),
        'user_roles': user.getRolesInContext(context),
        'user_first_name': first_name,
        'user_last_name': last_name,
        'email': email,
        'user_phone_number': phone_number
    }
    return json_response(response_data, request.RESPONSE)
