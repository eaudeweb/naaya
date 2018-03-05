for filter in filters:
    if kwargs.get('category'):
        filter['category'] = kwargs.get('category')
    if kwargs.get('sustainability'):
        filter['sustainability'] = kwargs.get('sustainability')
    if kwargs.get('credibility'):
        filter['credibility'] = kwargs.get('credibility')
    if kwargs.get('certificate_services'):
        filter['certificate_services'] = kwargs.get('certificate_services')
return filters
