Naaya Calendar

	This product was designed to present the meetings and events published
	on a portal in calendar form.
	By default, the calendar displays the days of the current month; the
	ones in which meetings and events are scheduled appear with links to
	corresponding list. The current day appears in a different color.
	The user is able to navigate back and forward among months.
	When clicking on the name of a month, the whole list of items from
	that period is displayed.


	Usage

		The calendar will display objects of given metatypes.
		In order to specify those metatypes, enter the "Properties"
		tab of your calendar and fill the "Meta Types (to search for)"
		property.

		After you filled the "Meta Types (to search for)" at the
		bottom of the page you can set the date properties and
		visualisation condition for your objects.

		The "use catalog" property specifies the catalog used to
		search the objects displayed by the calendar.

		The objects will be included in the calendar based on some
		date properties (e.g. "resource_date" and "resource_end_date")
		and a visualisation condition. A DateRangeIndex for these date
		properties will need to be added to the catalog.
		The "visualisation condition" properties is empty by default,
		so it will be ignored.

		According to your needs you can fill "start date" and
		"end date" with a date type property name of the defined
		object and in "visualisation condition" field you can put a
		python expression like "self.approved" or "self.getApproved()"
		to be evaluated.




	Look & feel

		**Important note:** when you add a calendar instance on a page
		of your portal, make sure you include its stylesheet in the
		header of the page. The URL of the stylesheet is ``string:${here/absolute_url}/calendar_style``.

		The calendar can be easily integrated in any portal's
		look&feel by changing it's appearance (fonts, colors, borders,
		title,...) from the "Calendar style" and "Events style" tabs.

		The EventCalendar folder contains two images (left_arrow and
		right_arrow) for the two arrows, left and right, used to
		browse back and forward among the months. Upload them
		according to your website colors. Also there is locatated the
		calendar's CSS file which can be modified.

		As default, EvenCalendar's template uses
		"standard_html_header" and "standard_html_footer", if you want
		to integrate it in other type of template you must modify the
		following files:
		- calendar_month_events.zpt (just change the first and the last line)
		- calendar_day_events.zpt (just change the first and the last line)
		- calendar_template.zpt (only if you really need to change something).

		This files can be found on your file system into Zope's
		products folder e.g. "..\Products\NaayaCalendar\zpt" folder.
