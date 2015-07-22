howmany = -1
if context.numberofitems != 0: howmany = context.numberofitems
return context.getCatalogedObjectsCheckView(meta_type='Naaya Event', approved=1, howmany=howmany)
