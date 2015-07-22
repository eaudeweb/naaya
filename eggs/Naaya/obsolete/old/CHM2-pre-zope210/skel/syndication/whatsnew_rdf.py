r = [x for x in context.getNewsArchive().objectValues(context.get_constant('METATYPE_NYNEWS')) if x.approved==1 and x.topitem==1 and x.submitted==1]
r.sort(lambda x,y: cmp(y.releasedate, x.releasedate) or cmp(x.sortorder, y.sortorder))
return r
