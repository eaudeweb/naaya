howmany = -1
if context.numberofitems != 0: howmany = context.numberofitems
return context.getCatalogedObjectsCheckView(meta_type=context.get_constant('METATYPE_NYEVENT'), approved=1, howmany=howmany)
