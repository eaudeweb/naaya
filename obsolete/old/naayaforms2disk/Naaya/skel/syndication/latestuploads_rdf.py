howmany = -1
if context.numberofitems != 0: howmany = context.numberofitems
return context.getCatalogedObjectsCheckView(meta_type=context.get_meta_types(), approved=1, howmany=howmany, path=['/'.join(x.getPhysicalPath()) for x in context.getMainTopics()])