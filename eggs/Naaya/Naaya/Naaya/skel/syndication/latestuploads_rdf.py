howmany = -1
if context.numberofitems != 0: howmany = context.numberofitems + 10
#dirty trick: we retrieve with 10 more results and we hope that eliminating
#protected items will have at least 'numberofitems' number of items
#otherwise will be fewer
r = []
for x in context.getCatalogedObjects(meta_type=context.get_meta_types(), approved=1, howmany=howmany, path=['/'.join(x.getPhysicalPath()) for x in context.getMainTopics()]):
    if x.checkPermissionView():
        r.append(x)
        if howmany != -1 and len(r)>context.numberofitems:
            break
return r