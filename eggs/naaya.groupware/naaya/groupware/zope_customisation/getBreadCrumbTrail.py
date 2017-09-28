request = container.REQUEST
breadcrumbs = []
PARENTS = request.PARENTS[:]

for crumb in PARENTS:
    breadcrumbs.append(crumb)
breadcrumbs.reverse()
return breadcrumbs
