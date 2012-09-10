1.2.15 (unreleased)
-------------------

1.2.14 (2012-09-10)
-------------------
* fix survey redirect condition [dumitval]

1.2.13 (2012-09-10)
-------------------
* Improvements in survey integration [dumitval] 

1.2.12 (2012-04-27)
-------------------
* bugfix: AttributeError: generate_csv [nituacor]

1.2.11 (2012-01-13)
-------------------
* Added i18n id for translation of 'Type' [dumitval]

1.2.10 (2011-11-17)
-------------------
* portal_map methods are no longer called if the content type is not
  geo_enabled [dumitval]

1.2.9 (2011-11-14)
------------------
* permission information update [andredor]

1.2.8 (2011-10-24)
------------------
* use reCAPTCHA for add forms [andredor]

1.2.7 (2011-04-12)
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
