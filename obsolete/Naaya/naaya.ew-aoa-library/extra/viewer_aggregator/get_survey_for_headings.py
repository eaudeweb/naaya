cf_v = container.aq_parent['country-fiches-viewer']
vl_v = container.aq_parent['virtual-library-viewer']

cf = cf_v.target_survey()
vl = vl_v.target_survey()

return {
'Section in State of Environment report': [vl],
'Section in environmental performance review': [vl],
'State of water assessment/report': [vl],
'Green economy assessment/report': [vl],
'Sectorial report': [vl],
'Water sector or NGOs report': [vl],
'Water statistics': [vl, cf],
'Environmental statistics': [vl, cf],
'Environmental indicator set': [vl, cf],
'Environmental compendium': [vl, cf],
'Water indicator set': [vl, cf],
'Website': [cf],
'Library services': [cf],
'Country profiles': [cf],
'National Institution dealing with water': [cf],
'National Institution dealing with green economy': [cf],
}
