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

return group_by_document_type
