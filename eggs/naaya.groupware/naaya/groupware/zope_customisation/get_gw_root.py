## Script (Python) "get_gw_root"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=ob=False
##title=
##
if ob: return container
return container.absolute_url()
