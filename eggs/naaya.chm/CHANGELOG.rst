3.0.27 (unreleased)
------------------
* re-encode mainsection images to jpeg if uploaded BMP or TIFF [dumitval]

3.0.26 (2014-07-10)
------------------
* `update` add i18n tags to the cookie disclaimer message [dumitval]

3.0.25 (2013-11-05)
------------------
* bugfix in admin_slider_image [dumitval]

3.0.24 (2013-07-26)
------------------
* removed jquery js, the one from Naaya should be used [dumitval]

3.0.23 (2013-05-20)
------------------
* template fix [dumitval]

3.0.22 (2013-05-20)
------------------
* template fix [dumitval]

3.0.21 (2013-05-20)
------------------
* support for reCAPTCHA keys from buildout [dumitval]

3.0.20 (2013-03-15)
------------------
* main_section_images Saved changes message + small bugfix [dumitval]

3.0.19 (2013-03-14)
------------------
* main section images inheritance [dumitval]

3.0.18 (2013-03-13)
------------------
* slider images management + update script [dumitval]

3.0.17 (2013-03-06)
------------------
* Update script to add cookie disclaimer message [dumitval]
* Added cookie disclaimer message to CHM3 [dumitval]

3.0.16 (2013-02-15)
------------------
* error handling in links_group_html [dumitval]

3.0.15 (2013-02-06)
------------------
* links_group_html error handling [dumitval]
* new icon for NyFolder [simiamih]
* show images in homepage slider in alphabetical order [dumitval]

3.0.14 (2012-07-31)
------------------
* Zope 2.10 fix for loading maintopic images [dumitval]

3.0.13 (2012-07-26)
------------------
* added translation flags to element_header [dumitval]

3.0.12 (2012-07-24)
------------------
* changed main section images for chm3 [dumitval]

3.0.11 (2012-07-24)
------------------
* Removed height on maintopics bar [dumitval]
* Added missing classes for floats [bogdatan]

3.0.10 (2012-06-29)
------------------
* Added folder_index to chm2 skel (temporary) [dumitval]
* All Naaya Skins and images removed before skel loading [dumitval]
* Added ie7,8,9 css files [dumitval]
* Removed some in-line style from element_spash_content [dumitval]

3.0.9 (2012-06-25)
------------------
* changed to use http_proxy from buildout [dumitval]

3.0.8 (2012-06-19)
------------------
* Fixed portlet_calendar to show in folders [dumitval]
* External link for recaptcha [dumitval]

3.0.7 (2012-06-12)
------------------
* bugfix in get_mainsection [dumitval]

3.0.6 (2012-06-08)
------------------
* Updated skel to rename images [dumitval]

3.0.5 (2012-06-08)
------------------
* renamed main section images [dumitval]

3.0.4 (2012-06-08)
------------------
* Mainsection images are shown also in subfolders [dumitval]

3.0.3 (2012-06-07)
------------------
* Updated some portlets to not show when empty [dumitval]
* Deleted site_index from skel-chm3/forms [dumitval]
* Updated 3.0 styles [dumitval]

3.0.2 (2012-04-23)
------------------
* Updated administration portlet with comments management section
  and API keys status section [bogdatan]
* admin main section images refactored admin interface [catardra]

3.0.1 (2012-03-12)
------------------
* tweaks to initial portal content [moregale]

3.0.0 (2012-03-12)
------------------
* for new portals create a top-level PhotoGallery instead of a
  PhotoFolder [moregale]
* enable monthly notifications by default [moregale]
* configurable resolution for mainsection images [moregale]
* new CHM3 layout ready to use [moregale]

2.4.20 (2012-03-12)
-------------------
* path correction for social icons in style_common [dumitval]
* New bundle "CHM3" with separate skel folder and new layout
  requires Naaya >= 2.12.52 [moregale]

2.4.19 (2011-12-16)
-------------------
* static resources for CHM3 layout

2.4.18 (2011-12-08)
-------------------
* geo coverage continents translations for french for new sites [andredor]
* convert geo coverage glossary import from xml for new sites [andredor]
* Possibility to add main_section images in custom sizes [dumitval]

2.4.17 (2011-11-16)
-------------------
* tag cloud portlet for chm terms [andredor]

2.4.16 (2011-11-10)
-------------------
* Replace glossary_keywords by chm_terms in menunav links [dumitval]
* new folder icon and sitemap fix [andredor]

2.4.15 (2011-11-09)
-------------------
* filter display for User management search [andredor]
* removed workgroup pages from User management [andredor]

2.4.14 (2011-10-31)
-------------------
* customize sitemap.xml form for CHM network

2.4.13 (2011-10-31)
-------------------
* removed form languages_box.zpt from skel/forms - identical to Naaya [dumitval]

2.4.12 (2011-10-28)
-------------------
* Owner can have just edit content permission (admin other properties) [andredor]
* standard templates updated to site logo changes [dumitval]
* css for layout with checkboxes in legend filters, portal_map [simiamih]
* updated chm terms with it translations [simiamih]

2.4.11 (2011-10-24)
-------------------
* removed dependency of Naaya Helpdesk Agent + update script [dumitval]
* remove processFeedbackForm customization [andredor]
* add admin_network_html to portlet_administration [andredor]
* portal_map css fixes for IE 7-9 [simiamih]

2.4.10 (2011-10-20)
-------------------
* removed admin_predefined_html (#707) [andredor]

2.4.9 (2011-10-19)
------------------
* add 'Folder subobjects' link to portal_administration [andredor]

2.4.8 (2011-10-19)
------------------
* removed glossaries tab from admin portal properties [dumitval]

2.4.7 (2011-10-19)
------------------
* portal_map css updated for the new and cleaner design [simiamih]

2.4.6 (2011-10-14)
------------------
* admin top content page [andredor]
* main topics admin page doesn't add/delete folders [andredor]
* portlet administration on disk for new semide sites [andredor]
* portlet administration also on disk [andredor]

2.4.5 (2011-10-11)
------------------
* Style improvements for indexes without right portlets [dumitval]

2.4.4 (2011-10-11)
------------------
* CHMSite no longer considered container #705 [simiamih]
* Fixed path of social icons (for folder index) to work for the existing CHMSites too [bogdatan]
2.4.3 (2011-10-11)
------------------
* adapted skel.nyexp to use the NaayaPageTemplate custom indexes for the News and Stories folders [dumitval]
* style improvements; icons for feeds, facebook and twitter (for folder
  index) [bogdatan]

2.4.2 (2011-10-06)
------------------
* Register templates in "CHM" bundle

2.4.1 (2011-09-23)
------------------
* CHM-EU migrated to egg installation
