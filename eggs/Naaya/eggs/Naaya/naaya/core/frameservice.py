from zope2util import json_response


def frame_view(context, request):
    # TODO unit tests
    # TODO documentation
    user = request.AUTHENTICATED_USER
    response_data = {
        'frame_html': context['frame.html'](),
        'user_id': user.getId(),
        'user_roles': user.getRolesInContext(context),
    }
    return json_response(response_data, request.RESPONSE)
