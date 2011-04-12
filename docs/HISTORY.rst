Changelog
=========

1.2.6 (2011-04-12)
--------------------
 * h:m:s doesn't match date index lookup for calendar, strip it

1.2.6 (2011-04-12)
--------------------
 * Indexing Adapter does not strip h:m:s (safer this way)

1.2.5 (2011-04-06)
--------------------
 * Adapter to allow catalogObject to access interval's start_date and end_date

1.2.4 (2011-03-30)
--------------------
 * Removed start_date, end_date, time properties
 * Added interval property, using IntervalWidget
 * ICalendar export is public, now exporting all day or datetime interval
 * More precise location in ICalendar export
 * Added description in ICalendar export with text and html (for outlook)
