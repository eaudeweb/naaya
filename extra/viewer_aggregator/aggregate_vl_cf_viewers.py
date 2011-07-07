cf_v = container.aq_parent['country-fiches-viewer']
vl_v = container.aq_parent['virtual-library-viewer']

cf = cf_v.target_survey()
vl = vl_v.target_survey()

cf_shadows = cf_v.filter_answers_cf_vl_aggregator(country, theme)
vl_shadows = vl_v.filter_answers_cf_vl_aggregator(country, theme)

group_by_document_type = {}
for shadow in cf_shadows:
    group_by_document_type.setdefault(shadow.document_type, []).append(shadow)
for shadow in vl_shadows:
    group_by_document_type.setdefault(shadow.document_type, []).append(shadow)

document_type_names = cf['w_type-document'].getChoices()
heading_document_types = container.heading_document_types()

ret = {}
for heading, document_types in heading_document_types.items():
    ret[heading] = {}
    for dt in document_types:
        dt_i = document_type_names.index(dt)
        if dt_i in group_by_document_type:
            ret[heading][dt_i] = group_by_document_type[dt_i]

ret = list(ret.items())
ret.sort()
return ret
