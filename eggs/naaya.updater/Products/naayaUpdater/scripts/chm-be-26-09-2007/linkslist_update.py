for portal in container.get_portals(exclude=False):
  portal_portlets = portal.portal_portlets

  if portal.id in ['test_maroc','bch-cbd']:
    portal.admin_addlinkslist(id='topnav_links', title='Top navigation links')
    ls_ob = portal.getPortletsTool().getLinksListById('topnav_links')
    ls_ob.manage_add_link_item(id="100", title="Biodiversity CHM", description="Global Biodiversity Clearing-House Mechanism (CBD)", url="http://www.biodiv.org/chm", relative="0", permission="", order="10")
    ls_ob.manage_add_link_item(id="101", title="Europa", description="Gateway to the European Union", url="http://europa.eu.int/", relative="0", permission="", order="20")
    ls_ob.manage_add_link_item(id="102", title="DG Environment", description="Directorate General Environment", url="http://europa.eu.int/comm/environment/index_en.htm", relative="0", permission="", order="30")
    ls_ob.manage_add_link_item(id="103", title="DG Env-Nature", description="Directorate General Environment-Nature", url="http://europa.eu.int/comm/environment/nature/home.htm", relative="0", permission="", order="40")
    ls_ob.manage_add_link_item(id="104", title="EEA", description="European Environment Agency", url="http://www.eea.eu.int/", relative="0", permission="", order="50")
    ls_ob.manage_add_link_item(id="105", title="GBIF", description="Global Biodiversity Information Facility", url="http://www.gbif.org/", relative="0", permission="", order="60")
    ls_ob.manage_add_link_item(id="106", title="EUNIS Database", description="European Nature Information System", url="http://eunis.eea.eu.int", relative="0", permission="", order="70")
    ls_ob.manage_add_link_item(id="107", title="SEBI", description="European Biodiversity Indicators 2010", url="/information/indicator/F1090245995", relative="1", permission="", order="80")
    ls_ob.manage_add_link_item(id="108", title="Biosafety BCH", description="Global Biosafety Clearing-House (CBD)", url="http://bch.biodiv.org/", relative="0", permission="", order="90")
    ls_ob.manage_add_link_item(id="109", title="EC ABS", description="EC Access and Benefit Sharing portal", url="/information/F1046684686/F1058442682/", relative="1", permission="", order="100")

  if portal.absolute_url(1) in ['zambia/mtenr','formation_chm_madagascar/mauritius','formation_chm_madagascar/madagasca','bch-cbd','test_layout_arnaud']:
    portal.admin_addlinkslist(id='menunav_services', title='Services')
    ls_ob = portal.getPortletsTool().getLinksListById('menunav_services')
    ls_ob.manage_add_link_item(id="110", title="Glossary", description="", url="/glossary_keywords", relative="1", permission="", order="110")
    ls_ob.manage_add_link_item(id="112", title="Other searches", description="", url="/external_search_html", relative="1", permission="", order="130")
    ls_ob.manage_add_link_item(id="109", title="Administration", description="", url="/admin_centre_html", relative="1", permission="", order="100")

    portal.admin_addlinkslist(id='menunav_content', title='Content')
    ls_ob = portal.getPortletsTool().getLinksListById('menunav_content')
    ls_ob.manage_add_link_item(id="102", title="News", description="News archive", url="/news/", relative="1", permission="", order="30")
    ls_ob.manage_add_link_item(id="103", title="Stories", description="Stories archive", url="/stories/", relative="1", permission="", order="40")
    ls_ob.manage_add_link_item(id="104", title="Events", description="Events archive", url="/events/", relative="1", permission="", order="50")
    ls_ob.manage_add_link_item(id="105", title="Photos", description="Photo archive", url="/PhotoArchive/", relative="1", permission="", order="60")

    portal.admin_addlinkslist(id='menunav_about', title='About')
    ls_ob = portal.getPortletsTool().getLinksListById('menunav_about')
    ls_ob.manage_add_link_item(id="107", title="About", description="", url="/About/", relative="1", permission="", order="80")

    portal.admin_addlinkslist(id='menunav_sitemap', title='Sitemap')
    ls_ob = portal.getPortletsTool().getLinksListById('menunav_sitemap')
    ls_ob.manage_add_link_item(id="108", title="Sitemap", description="", url="/sitemap_html", relative="1", permission="", order="90")

print 'Done.'
return printed
