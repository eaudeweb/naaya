1.2.41 (unreleased)
===================
* xlwt and xlrd added to Naaya as dependencies. No need to assert availability. [dumitval]

1.2.40 (2014-01-10)
===================
* customisations of the email templates [dumitval]

1.2.39 (2014-01-10)
===================
* remove anonymous from view reports permission [dumitval]

1.2.38 (2014-01-09)
===================
* Fix for survey reports with anonymous users [dumitval]

1.2.37 (2013-12-18)
===================
* Send notification to owner also for anonymous users + email formatting [dumitval] 

1.2.36 (2013-12-09)
===================
* added possibility to answer in a participant's name [dumitval]

1.2.35 (2013-09-26)
===================
* define a local messages_html (view permission issues) [dumitval]
* specify anonymous status in confirmation mail [dumitval]

1.2.34 (2013-08-30)
===================
* show signup respondent name from parent meeting, if applicable [dumitval]
* bugfix in anonymous aswering system [dumitval]

1.2.33 (2013-08-29)
===================
* allow auth. users to answer anonymously [dumitval]

1.2.32 (2013-07-26)
===================
* removed duplicated notification to maintainer [dumitval]

1.2.31 (2013-06-03)
===================
* label and text change for anonymous responder email [dumitval]

1.2.30 (2013-05-24)
===================
* now the contributor property is set [dumitval]
* skip messages_html when adding a survey [dumitval]

1.2.29 (2013-04-15)
===================
* added inherit_view_permission method [dumitval]

1.2.28 (2013-03-26)
===================
* bugifx in survey session [nituacor]

1.2.27 (2013-03-21)
===================
* redirect to the parent after answer submit ONLY IF IN MEETING [dumitval]
* small template improvements [dumitval]

1.2.26 (2013-02-28)
===================
* bugfix in combobox matrix widget [moregale]

1.2.25 (2013-01-09)
===================
* bugfix in answers export [dumitval]

1.2.24 (2012-12-07)
===================
* bugfix in sender_email getter [dumitval]

1.2.23 (2012-11-06)
===================
* bugfix: #9938; improper unauthorized error on rendering answer [simiamih]
* bugfix: #9933; CSS fix inside survey_common.css [soniaand]

1.2.22 (2012-10-03)
===================
* bugfix: #1000; fixed KeyError on rendering survey report [simiamih]

1.2.21 (2012-09-10)
===================
* redirect to the parent after answer submit [dumitval]

1.2.20 (2012-05-22)
===================
* Enhanced error messages for report generation [dumitval]

1.2.19 (2012-04-27)
===================
* bugfix: AttributeError: generate_csv [nituacor]

1.2.18 (2012-02-03)
===================
* bugfix: utf8 labels in graphs [simiamih]

1.2.17 (2012-01-31)
===================
* bugfix: missing i18n [nituacor]

1.2.16 (2012-01-13)
===================
* Added i18n id for translation of 'Type' [dumitval]
* removed .txt from manifest [dumitval]

1.2.15 (2012-01-06)
===================
* check_item_title is now item_has_title [simiamih]

1.2.14 (2012-01-06)
===================
* added can_be_seen for MegaSurvey [simiamih]

1.2.13 (2011-12-09)
===================
* TypeError: sequence expected, NoneType found [nituacor]

1.2.12 (2011-12-09)
===================
* TypeError: sequence expected, NoneType found [nituacor]

1.2.11 (2011-12-09)
===================
* fix MatrixWidget initial value [nituacor]

1.2.10 (2011-12-08)
===================
* fix multiple choice widget initial value [andredor]

1.2.9 (2011-11-14)
==================
* permission information update [andredor]

1.2.8 (2011-10-24)
==================
* use reCAPTCHA for add forms [andredor]
* remove show_captcha wrapper [andredor]

1.2.7 (2011-10-19)
==================
* bufgix: default value False for allow_multiple_answers #714 [simiamih]

1.2.6 (2011-10-18)
==================
* xlwt dependency, rel="nofollow" on export link [simiamih]
* Bugfix in RadioWidget.get_value
* Administrators can now edit answers in expired surveys

1.2.5 (2011-09-23)
==================
* Merge Products.NaayaSurvey and Products.NaayaWidgets into a single package
  named "naaya-survey"

1.2.2 (2011-04-28)
==================
* Last version where Products.NaayaSurvey and Products.NaayaWidgets were
  separate packages
