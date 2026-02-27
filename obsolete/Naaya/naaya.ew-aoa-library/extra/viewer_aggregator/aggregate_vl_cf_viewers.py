cf_v = container.aq_parent['country-fiches-viewer']
vl_v = container.aq_parent['virtual-library-viewer']

cf = cf_v.target_survey()
vl = vl_v.target_survey()

cf_shadows = cf_v.filter_answers_cf_vl_aggregator(int(country), theme)
vl_shadows = vl_v.filter_answers_cf_vl_aggregator(int(country), theme)

group_by_document_type = {}
for shadow in cf_shadows:
    for dt_i in shadow.document_type:
        dtn_i = cf_v.get_normalized_document_type(dt_i)
        group_by_document_type.setdefault(dtn_i, []).append(shadow)
for shadow in vl_shadows:
    for dt_i in shadow.document_type:
        dtn_i = vl_v.get_normalized_document_type(dt_i)
        group_by_document_type.setdefault(dtn_i, []).append(shadow)

document_type_names = cf_v.all_document_types
heading_document_types = container.heading_document_types()

group_by_heading = {}
for heading, document_types in heading_document_types.items():
    group_by_heading[heading] = []
    for dt in document_types:
        dt_i = document_type_names.index(dt)
        if dt_i in group_by_document_type:
            group_by_heading[heading].extend(group_by_document_type[dt_i])
    group_by_heading[heading].sort(key=lambda x: x.publication_year, reverse=True)

ret = []
if theme == 'Water':
    for heading in container.water_headings_in_order():
        if heading in group_by_heading and group_by_heading[heading]:
            ret.append((heading, group_by_heading[heading]))
else: # theme == 'Green Economy'
    for heading in container.ge_headings_in_order():
        if heading in group_by_heading and group_by_heading[heading]:
            ret.append((heading, group_by_heading[heading]))

return ret
