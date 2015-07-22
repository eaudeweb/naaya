id_prefix = 'deliverable-'
outputs = {}
errors = []
digit = '0123456789'

def deliverable_number(object_id):
    if (len(object_id) < 3) or (object_id[0] not in 'dD') or (object_id[1] not in digit) or (object_id[2] not in digit):
        return None
    return object_id[:3]

for object_id, obj in context.objectItems():
  try:
    dn = deliverable_number(object_id)
    if dn is None:
      continue
    obj_title = obj.title_or_id()
    if obj_title.lower().startswith(dn.lower()):
      obj_title = obj_title[len(dn):].strip()
    outputs.setdefault(dn, []).append({'title': obj_title, 'url': obj.absolute_url()})
  except Exception, e:
    errors.append( (object_id, str(e)) )

return {'outputs': outputs, 'errors': errors}
