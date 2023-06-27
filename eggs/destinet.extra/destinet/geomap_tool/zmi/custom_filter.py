for filter in filters:
    if kwargs.get('category'):
        filter['category'] = kwargs.get('category')
    if kwargs.get('sustainability'):
        filter['sustainability'] = kwargs.get('sustainability')
    if kwargs.get('credibility'):
        filter['credibility'] = kwargs.get('credibility')
    if kwargs.get('certificate_services'):
        filter['certificate_services'] = kwargs.get('certificate_services')
    if kwargs.get('gstc_criteria'):
        filter['gstc_criteria'] = kwargs.get('gstc_criteria')
    if kwargs.get('gstc_industry'):
        filter['gstc_industry'] = kwargs.get('gstc_industry')
    if kwargs.get('agenda2030_sdgs'):
        filter['agenda2030_sdgs'] = kwargs.get('agenda2030_sdgs')
return filters
