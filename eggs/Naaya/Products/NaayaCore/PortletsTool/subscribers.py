def update_assignments_after_move(event):
    """ object was renamed; update portlet assigments if needed """
    old_site_path = event.old_site_path
    new_site_path = event.new_site_path
    portlets_tool = event.context.getSite().getPortletsTool()

    _portlet_layout = portlets_tool._portlet_layout

    for old_key in _portlet_layout.keys():
        if old_key[0] == old_site_path:
            new_key = (new_site_path, old_key[1])
            _portlet_layout[new_key] = _portlet_layout[old_key]
            del _portlet_layout[old_key]
            portlets_tool._p_changed = True
