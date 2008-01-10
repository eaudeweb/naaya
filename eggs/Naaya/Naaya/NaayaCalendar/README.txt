<h1>The README file for Naaya Calendar</h1> 

<h3>Naaya Calendar</h3>
<p>
This product was designed to present the meetings and events published on a portal in calendar form.
By default, the calendar displays the days of the current month; the ones in which meetings and events are scheduled 
appear with links to corresponding list. The current day appears in a different color.
The user is able to navigate back and forward among months.
When clicking on the name of a month, the whole list of items from that period is displayed.
</p>


<h3>Usage</h3>
<p>
The calendar will display objects of given metatypes.
In order to specify those metatypes, enter the "Properties" tab of your calendar and fill the "Meta Types (to search for)"
property.
</p>

<p>
After you filled the "Meta Types (to search for)" at the bottom of the page you can set the date properties and
visualisation condition for your objects.
</p>

<p>The "use catalog" property if filled, will make the calendar to use the indicated catalog.
If left empty, Zope's "PrincipiaFind" function will be used for searching objects (more time consuming).
</p>

<p>
The objects will be included in the calendar based on some date property and a visualisation condition.
By default, "start_date" value is taken for "start date" property and "end_date" for "end date" property.
The "visualisation condition" properties by default is empty and ignored.
</p>

<p>
According to your needs you can fill "start date" and/or "end date" with a date type property name of the defined object and in
"visualisation condition" field you can put a python expression like "self.approved == 1" or "self.getApproved() == 1" to
be evaluated.

If "start date" is left empty, "bobobase_modification_time" will be set automatically.
</p>

<p>
Into "Warnings" fields you'll find a general message regarding that property of object such:
<dl>
	<dd>"Property found"</dd>
	<dd>"No such property"</dd>
	<dd>"Empty"</dd>
	<dd>"No object found".</dd>
</dl>
</p>

<h3>Look&feel</h3>

<p><strong>Important note:</strong> when you add a calendar instance on a page of your portal, make sure you include its stylesheet in the header of the page:
</p>

<code>&lt;link rel="stylesheet" type="text/css" tal:attributes="href string:${here/getEventCalendarURL}/calendar_style" /&gt;</code>

<p>
The calendar can be easily integrated in any portal's look&feel by changing it's appearance
(fonts, colors, borders, title,...) from the "Calendar style" and "Events style" tabs.
</p>

<p>
The EventCalendar folder contains two images (left_arrow and right_arrow) for the two arrows, left and right,
used to browse back and forward among the months. Upload them according to your website colors. Also there is
locatated the calendar's CSS file which can be modified.
</p>

<p>
As default, EvenCalendar's template uses "standard_html_header" and "standard_html_footer", if you want to integrate it
in other type of template you must modify the following files:
<dl>
	<dd>calendar_month_events.zpt (just change the first and the last line)</dd>
	<dd>calendar_day_events.zpt (just change the first and the last line)</dd>
	<dd>calendar_template.zpt (only if you really need to change something).</dd>
</dl>
This files can be found on your file system into Zope's products folder e.g. "..\Products\EventCalendar\zpt" folder.
</p>
