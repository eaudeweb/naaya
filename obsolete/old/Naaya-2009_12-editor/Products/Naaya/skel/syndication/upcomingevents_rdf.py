r, d = [], context.utGetTodayDate()
ra = r.append
for e in context.getCatalogedObjectsCheckView(meta_type='Naaya Event', approved=1):
    if e.start_date > d: ra(e)
return r
