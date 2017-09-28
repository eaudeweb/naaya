howmany = -1
if context.numberofitems != 0: howmany = context.numberofitems
return context.rstk['latest_visible_uploads'](howmany)
