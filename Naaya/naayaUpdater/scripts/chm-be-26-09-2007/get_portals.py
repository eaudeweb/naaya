#exclude=True
EXCLUDE_LIST = ['bch-cbd','test_layout_arnaud','maroc2','comifac_dev']

res = []
root = container.aq_parent

for chm_site in root.objectValues("CHM Site"):
    if (exclude == True) and (chm_site.id in EXCLUDE_LIST):
        pass
    else:
        res.append(chm_site)
    for secondary_chm_site in chm_site.objectValues("CHM Site"):
        if (exclude == True) and (chm_site.id in EXCLUDE_LIST):
            pass
        else:
            res.append(secondary_chm_site)

return res
