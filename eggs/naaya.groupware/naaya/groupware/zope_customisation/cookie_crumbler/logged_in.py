request = container.REQUEST
RESPONSE =  request.RESPONSE
came_from = request.get('came_from', '../index_html')

if request.AUTHENTICATED_USER.getUserName() == 'Anonymous User':
    RESPONSE.unauthorized()
    return RESPONSE.redirect('./login_form?came_from=%s' % came_from)
elif came_from:
    return RESPONSE.redirect(came_from)
