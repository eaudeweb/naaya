1.2.93 (unreleased)
-------------------
* added support for the verbose edw version of validate_email [dumitval]

1.2.92 (2016-07-26)
-------------------
* fix an error with mixed ascii and utf8 strings [dumitval]

1.2.91 (2016-02-24)
-------------------
* fix textarea resize in IE [dumitval]

1.2.90 (2016-02-11)
-------------------
* set duration interval for the eionet meetings automatic survey +
  update script [dumitval]

1.2.89 (2016-01-28)
-------------------
* fix in question order of the eionet meeting survey [dumitval]

1.2.88 (2016-01-26)
-------------------
* structural changes to the automatic surveys for Eionet meetings [dumitval]

1.2.87 (2015-11-10)
-------------------
* add "I prefer not to answer" option on radio button questions of
  Eionet surveys (incl. update script) [dumitval]

1.2.86 (2015-10-28)
-------------------
* bugifx in automatic survey generation [dumitval]

1.2.85 (2015-10-07)
-------------------
* fix for excel export of participants in meetings with mandatory survey
  [dumitval]
* remove testing for disabled@eionet.europa.eu when searching for users
  (they are filtered in the search method) [dumitval]

1.2.84 (2015-09-14)
-------------------
* add email in search by role user details (add signup) [dumitval]

1.2.83 (2015-08-19)
-------------------
* fix for signup approve/reject [dumitval]

1.2.82 (2015-07-03)
-------------------
* removed the export for webex, will be replaced by Skype [dumitval]

1.2.81 (2015-06-26)
-------------------
* export participants for webex [dumitval]

1.2.80 (2015-06-22)
-------------------
* released production version

1.2.80-test (2015-06-10)
-------------------
* `update` introduced several meeting types + their standard surveys [dumitval]

1.2.79 (2015-05-28)
-------------------
* user-related utils moved to Naaya Authentication Tool [dumitval]

1.2.78 (2015-05-25)
-------------------
* unify applications listing [dumitval]

1.2.77 (2015-05-20)
-------------------
* now survey required without pointer to survey [dumitval]

1.2.76 (2015-05-18)
-------------------
* bugfix: allow new line in textarea [dumitval]
* specific error messages in email seding form [dumitval]
* changes in mail_in_queue logic to support separate emails to signups
  [dumitval]
* mail format verification for CC field [dumitval]

1.2.75 (2015-05-07)
-------------------
* correct bulk download link [dumitval]

1.2.74 (2015-04-29)
-------------------
* `update` script for meeting schema (pointer relative) [dumitval]
* hide disabled users from the user search results (add signup, send
  emails) [dumitval]
* JQuery Eionet user search in email sending [dumitval]
* send signup notification also to the user who created the signup (if
  different than the singup person) [dumitval]
* send auth key to signups when linking meeting documents [dumitval]
* allow reimbursed status also without country (for admins) [dumitval]
* delete the 'reimbursed' status when rejecting participants [dumitval]

1.2.73 (2015-04-15)
-------------------
* handle case when mandatory survey is missing (email archive) [dumitval]

1.2.72 (2015-04-07)
-------------------
* decode subject in archive listing for subjects longer than 75
  characters [dumitval]

1.2.71 (2015-04-01)
-------------------
* add the answers from the mandatory survey to the participants export
  to Excel [dumitval]

1.2.70 (2015-03-30)
-------------------
* bugfix in resending emails to participants [dumitval]

1.2.69 (2015-03-26)
-------------------
* removed the extra columns (survey) from participants listing [dumitval]
* option to resent confirmation emails to participants [dumitval]

1.2.68 (2015-03-19)
-------------------
* once validated, reCaptcha will not reappear in the session (meeting
  only) [dumitval]
* reCaptcha 2.0 compatibility [dumitval]

1.2.67 (2015-03-10)
-------------------
* bugfix related to authenticated users adding signups [dumitval]

1.2.66 (2015-02-26)
-------------------
* support redirect from welcome page (signup authentication) [dumitval]
* get authenticated signup details [dumitval]
* authenticate signups even before approval [dumitval]

1.2.65 (2015-02-20)
-------------------
* authenticate as signup right after registration [dumitval]

1.2.64 (2015-02-19)
-------------------
* redirect successful signup authentication to the meeting index [dumitval]

1.2.63 (2015-01-30)
-------------------
* Use uid when getting user full name fails [dumitval]

1.2.62 (2015-01-29)
-------------------
* bugfix related to anonymous subscriptions [dumitval]

1.2.61 (2014-11-10)
-------------------
* bugfix related to eionet_meeting default survey creation [dumitval]
* pep8 code formatting [dumitval]

1.2.60 (2014-09-26)
-------------------
* change Excel export filname to include meeting id and download date [dumitval]

1.2.59 (2014-09-26)
-------------------
* added new columns to the participants Excel export [dumitval]
* corrected country code for Iceland, added country code for Ireland [dumitval]

1.2.58 (2014-09-19)
-------------------
* administrators can set country representation and reimbursement [dumitval]

1.2.57 (2014-06-11)
-------------------
* Bug fix: fix signup to workshop
* Bug fix: fix tests for access to meetings based on release date 
  [tiberich #18783]

1.2.56 (2014-05-06)
-------------------
* bugfix in assiging 'representative' status for signups before approval [dumitval]

1.2.55 (2014-04-07)
-------------------
* Task #17799 - choose emails to export to xcel [baragdan]

1.2.54 (2014-03-18)
-------------------
* fixed xcel typo [dumitval]
* Feature: make meetings private when the release date is in the future;
  Automatically approve them when the release date has passed
  [tiberich #18783]

1.2.53 (2014-02-07)
-------------------
* Default eionet survey, with questions, custom validation, default status, sort order [dumitval]

1.2.52 (2014-01-20)
-------------------
* insert links to meeting objects in mails to participants [dumitval]

1.2.51 (2014-01-07)
-------------------
* task 17799 - export mail list to xcel [baragdan]

1.2.50 (2013-12-18)
-------------------
* class-based selection of cells with emails to be validated [dumitval]
* added cc field in email sending interface [dumitval]

1.2.49 (2013-12-11)
-------------------
* Email Validation - resolve validation in backend threads (avoid server load) [baragdan]

1.2.48 (2013-12-09)
-------------------
* Email Validation - controll js parallelism (avoid server load) [baragdan]

1.2.47 (2013-12-05)
-------------------
* email validation [baragdan]
* _mail_in_queue moved to EmailTool [dumitval]

1.2.46 (2013-11-11)
-------------------
* show if mail is still in mail_queue, or even failed sending [dumitval]

1.2.45 (2013-11-08)
-------------------
* save sent mails in an archive + listing [dumitval]

1.2.44 (2013-11-01)
-------------------
* updated script changed to not sent user notifications [dumitval]

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
