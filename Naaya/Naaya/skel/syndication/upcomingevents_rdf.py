r, d = [], context.utGetTodayDate()
ra = r.append
for e in context.getCatalogedObjects(meta_type=context.get_constant('METATYPE_NYEVENT'), approved=1):
    if e.start_date > d: ra(e)
return r
