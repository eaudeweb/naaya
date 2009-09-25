portals = container.objectValues('Groupware site')
sorted = {}
for portal in portals:
    sorted.setdefault(portal.get_user_access(), []).append(portal)
return sorted
