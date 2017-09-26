request = container.REQUEST
RESPONSE =  request.RESPONSE

return RESPONSE.redirect(container.absolute_url() + '/login_form')
