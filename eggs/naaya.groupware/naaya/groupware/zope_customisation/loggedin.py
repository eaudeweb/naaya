request = container.REQUEST
RESPONSE =  request.RESPONSE

return RESPONSE.redirect(request.get('HTTP_REFERER'))
