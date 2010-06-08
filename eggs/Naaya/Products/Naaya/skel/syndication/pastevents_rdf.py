r, d = [], context.utGetTodayDate()
ra = r.append
for e in context.getCatalogedObjectsCheckView(meta_type='Naaya Event', approved=1):
    if e.start_date < d-1: ra(e)
return r
