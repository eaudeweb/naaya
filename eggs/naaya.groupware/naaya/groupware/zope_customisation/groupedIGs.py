portals = container.objectValues('Groupware site')
sorted = {}
for portal in portals:
    if portal.portal_is_archived:
        sorted.setdefault('archived', []).append(portal)
    else:
        sorted.setdefault(portal.get_user_access(), []).append(portal)

for portal_list in sorted.values():
    portal_list.sort(key=lambda p: p.title_or_id())

return sorted
