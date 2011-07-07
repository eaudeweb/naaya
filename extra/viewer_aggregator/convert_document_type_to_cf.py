document_type_names = container.document_types()

site = container.getSite()

cf_v = site['country-fiches-viewer']
cf = cf_v.target_survey()
cf_document_types = cf['w_type-document'].getChoices()

ret = []
for i, dt in enumerate(document_type_names):
    if dt in cf_document_types:
        ret.append(cf_document_types.index(dt))
    else:
        ret.append(0)
return ret
