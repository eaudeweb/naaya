Stylesheets
===========

.. note::

   This document describes an ideal scenario. Current Naaya sites in production
   don't conform to this layout, but they should get there sometime soon.

CSS files
---------

Style rules in Naaya are spread over several files:

`common`
  Simple rules that apply in any context. Useful for custom elements (a link
  that looks like a button; a list whose elements are floated) and styles for
  administrative pages that don't need to be skinned. Print rules should also
  go here.

  `common` files are loaded from disk and live in the ``www`` folder of a
  package. Add-on products may register their own `common` files which are
  concatenated and served as a single HTTP resource.

`skin`
  Custom look for a site or family of sites. All skins are based on roughly the
  same HTML markup, but are free to style the elements however they need.

  `skin` files are loaded into the database when a site is created, as part of
  ``skel``. Because they only reflect a site's visual design, they should
  require few updates as new features are developed.

`color`
  Each skin has one or more color schemes. These are typically small, only
  declaring a few color and image rules.


Useful HTML IDs and classes
---------------------------

.. code-block:: css

    /* right-side portlets */
        #right_port, .right_link_portlet, .portlet-title
    /* errors and messages box */
        .system-msg
    /* Operations buttons */
        .floated-buttons, .submission_button, .buttons
    /* object administration (folder and subobjects) */
        #admin_this_folder
    /* second administration menu */
        #toolbar
    /* sub-objects listing */
        #folderfile_list
    /* Object language availability (item only translated in...) */
        .available_langs
    /* Tabbed menus  */
        #tabbedmenu, .tabbedmenu, .tabs_firstlevel, .second_tab_set
    /* warning box for active versions of items, placed inside the object's
       forms for editing on a version */
        .version_box
    /* Content translation boxes - present each form for individual item
       translation, such as Naaya News or HTML Portlet */
        .edit-holder, .translate, .edit_right_box
    /* add/edit forms */
        .field, .field-inline, .field label, .form-field, .form-fieldset
    /* comments on content */
        .comment_box, .deletecomment, .addcomment, .logincomment,
        .commentbox_title, .commentbox_content, .commentbox_add,
        .hr_addcomment, .hr_inside_comment
    /* sortable tables */
        .sortable /* obsolete */
    /* users and roles listing */
        .roles_per_folder, .folder_of_roles, .list_of_roles
    /* Pop up windows used as pickers */
        .pick_pop_up
    /* Thesaurus style */
        .h2term, .bar, .item_term, .tab_term, .th_cat
    /* Feeds */
        div.xmlExportButtons
    /* calendars & clocks */
        .calendarbox, .clockbox, .calendar
    /* Map styles */
        div.marker, div.marker-more, div.marker-body, .map-button,
        #record_counter_message
    /* forum styles */
        .message_top_buttons, .message_top_buttons2, .forum_*
