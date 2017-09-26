request = container.REQUEST
RESPONSE =  request.RESPONSE

if request.AUTHENTICATED_USER.getUserName() == 'Anonymous User':
    return RESPONSE.redirect('../index_html')

else:
    return RESPONSE.redirect('../manage_zmi_logout')
