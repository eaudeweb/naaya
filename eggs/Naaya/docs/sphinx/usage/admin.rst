Administration
==============

*Naaya* contains an administration section that can be used by administrators
to manage a Naaya site. **add a screenshot of the admin**

The Administration area (*Portal administration centre*) is provided to facilitate users with the
role of administrator to make basic maintenance operations and customisations of their portal.
Administrators are intended to be users with full decisional rights over the content and presentation
of the portal.

After logging in with the proper right, you can reach the Administration area by selecting the
Administration option from the top services links list. In here, all functionalities are listed in
the right-side Administration portlet.

* Add some reference to the roles document (and tell people that they need an admin account to use the admin).
* Describe here a few words about all administration sections.

The portal administration area contains a set of forms for:

* setting various *portal-level properties* such as
	* metadata: site title and subtitle, description (which appears on the front page of the portal), publisher, contributor, creator, rights
	* the two upper logos: for the left and right side of the top banner; different logos can be selected for different languages
	* email settings: containing the mail server used to send mails, the address from which the mails are sent, the list of emails of people that want to receive upload notifications and notifications on errors
	* glossaries: keywords glossary, a glossary of terms used to index the content by filling in the keywords property of each item; coverage glossary, containing geographical regions and countries, used to fill in the ``geographical coverage`` property of each item
	* various other properties relevant for the entire portal
* portal *statistics*, in order to access the statistics provided by Google Analytics for your portal; visits on a certain range of time, top pages visited, top searches in the portal, top referrers; the interval between which the portal statistics should be shown is set here, as well as the default account
* portal *layout customisation*, which allows choosing from a set of predefined layouts and colour schemes
* *users' management*, which allows managing users and their roles
* *translation centre* for the messages across the portal, with the possibility to individually translate items or import/export all the translation in CSV, XLIFF and PO formats;
* managing the *lists of links* that appear in the header and footer of each page, and in list of links portlets
* *selection lists*, which appear when adding/editing content types (e.g. when adding an event, there is a choice asking for the type of event; these choices can be set in the corresponding selection list)
* *notifications*, which are sent to subscribed users whent content iss added or modified in the portal
* *map management*, which allows managing the settings of the portal map and of the geo-tagged content, such as map height, choice of map engine; managing the types of locations which can be added for geo-taggable objects; managing locations
* *content management*
	* *manage content types*, which exposes all content types available in the portal, allows the configuration of the content type's properties, and also allows portals administrators decide whether content types available in the portal are geo-tagged and ratable.
	* overall *basket of approvals*, which lists pending (not yet approved) items from the portal
	* *basket of translations*, which lists the portal folders that contain items not yet translated into the specified language
	* *version control*, which displays a list of all objects checked out for editing by various users
	* management of the *main sections* that are listed in the left portlet; the *navigation properties* allows administrators to set the default style of navigation in the portal; in this respect, they can choose whether to have an expanded menu (main sections) or not, as well as to keep it like that, even after a user has clicked on a main section and has seen its folders and sub-folders and then went to another main section; the expand levels option allows administrators to specify the depth of the expanded navigation tree, and the maximum levels option allows administrators to specify the maximum depth of the navigation tree
* *syndication* allows defining and managing local and remote channels in Atom and RDF formats
	* the *Remote channels* section lists the remote channels defined by portal administrators; a cron service updates the feeds four times a day (every 6 hours), and they can also be manually updated, by pushing the *Update now* button
	* the *Remote channels aggregators* can be defined by the portal administrator and are collections of remote channels that contain all the data from the channels defined in the *Remote channels* section
* *portlets* - define, edit or delete them and arrange existing portlets around the pages
