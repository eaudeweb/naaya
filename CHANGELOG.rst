1.2.44 (unreleased)
-------------------

1.2.43 (2013-10-22)
-------------------
* fix for meeting listing in case of viewer role [dumitval]

1.2.42 (2013-10-15)
-------------------
* several test fixes
* `update` view permission for OBSERVER and WAITING roles [dumitval]
* `update` NFPs get access to participants and subscribers listings [dumitval]
* `update` all participants are now either signups or subscribers [dumitval]

1.2.41 (2013-09-03)
-------------------
* added option to search and signup users (as authenticated) [dumitval]

1.2.40 (2013-07-10)
-------------------
* link from meeting index to contributor's user profile [dumitval]
* Javascript fix in meeting edit [dumitval]

1.2.39 (2013-05-14)
-------------------
* #14435 if owner sets himself as participant, ownership is lost [simiamih]

1.2.38 (2013-03-29)
-------------------
* load default meta_types for new meeting [mihaitab]

1.2.37 (2013-03-26)
-------------------
* revert deleted session [nituacor]

1.2.36 (2013-03-21)
-------------------
* permission fix for meetings added by contributors [simiamih]
* bugfix in meeting list participants [mihaitab]
* clear session on meeting index [mihaitab]

1.2.35 (2013-03-18)
-------------------
* fixed form fields dependancy in add/eddit meeting [mihaitab]

1.2.34 (2013-03-14)
-------------------
* bugfix in participants sorting [dumitval]
* changed labels for geo_type and interval schema fields [mihaitab]

1.2.33 (2013-03-06)
-------------------
* removed portlet within the meeting index [dumitval]

1.2.32 (2013-03-06)
-------------------
* fixing owner needs to be able to manage meeting [simiamih]

1.2.31 (2013-02-26)
-------------------
* temp fix: meeting owner becomes Administrator of the meeting [simiamih]

1.2.30 (2012-12-10)
-------------------
* fixed bug - get missing email field for non-ldap users [mihaitab]

1.2.29 (2012-12-07)
-------------------
* fixed missing results in participants tab of a new meeting [mihaitab]
* fixed decoding in participants tab of a new meeting [mihaitab]

1.2.28 (2012-11-29)
-------------------
* i18n:name correction [dumitval]

1.2.27 (2012-11-28)
-------------------
* Translate email messages [dumitval]

1.2.26 (2012-11-28)
-------------------
* Add organisation and phone data also on AccountSubscriptions [dumitval]

1.2.25 (2012-11-27)
-------------------
* Show survey answers also in signup listing [dumitval]
* Hide specific survey questions from all listings (organisation, phone) [dumitval]
* Hide survey questions with ids starting with 'hide_' from all listings [dumitval]
* Get organisation and phone info from all possible sources [dumitval]

1.2.24 (2012-11-26)
-------------------
* Added some missing translation tags [dumitval]

1.2.23 (2012-11-22)
-------------------
* Added some missing translation tags [dumitval]

1.2.22 (2012-11-22)
-------------------
* Added some missing translation tags [dumitval]

1.2.21 (2012-11-21)
-------------------
* Added some missing translation tags [dumitval]

1.2.20 (2012-11-20)
-------------------
* redirect to survey also for key-based-participants [dumitval]

1.2.19 (2012-11-20)
-------------------
* Added some missing translation tags [dumitval]

1.2.18 (2012-10-22)
-------------------
* bugfix: #1013 using survey widget's get_value
  to get printable answer value [simiamih]

1.2.17 (2012-09-11)
-------------------
* bugfix in survey identification process [dumitval]

1.2.16 (2012-09-11)
-------------------
* List survey answers in the participants and applicants tables [dumitval]

1.2.15 (2012-09-10)
-------------------
* redirect to survey also for administrators [dumitval]

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
