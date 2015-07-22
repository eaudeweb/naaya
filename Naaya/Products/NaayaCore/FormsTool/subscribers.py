""" ITemplate subscribers.
If a PageTemplate that implements ITemplate is added to the portal_forms's OFS
then register that template instance to the local site manager.
The same idea applies for the rest of the CRUD.
"""
from interfaces import ITemplate

def template_added(context, event):
    """ Register only for `portal_forms` here """
    if (hasattr(context, 'aq_parent') and
        context.aq_parent == context.getSite().getFormsTool()):
        sm = context.getSite().getSiteManager()
        tmpl = event.object.aq_base
        sm.registerUtility(tmpl, ITemplate, event.object.__name__)

def template_before_remove(context, event):
    """ Unregister the template from local site manager, but only for
    `portal_forms` """
    if (hasattr(context, 'aq_parent') and
        context.aq_parent == context.getSite().getFormsTool()):
        sm = context.getSite().getSiteManager()
        tmpl = event.object.aq_base
        sm.unregisterUtility(tmpl, ITemplate, event.object.__name__)

