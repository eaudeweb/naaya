1.4.35 (unreleased)
-------------------
* Add files to consultation [dumitval]

1.4.34 (2014-08-21)
-------------------
* Bug fix: make a red message when previewing a file about needing to reupload file
  [tiberich #20725]

1.4.33 (2014-07-28)
-------------------
* Send emails from within the consultation, save them in archive [dumitval]

1.4.32 (2014-04-07)
-------------------
* Task #17799 - choose emails to export to xcel [baragdan]
* fixed xcel typo [dumitval]

1.4.31 (2014-01-17)
-------------------
* hide "Reply" button if the user doesn't have commenting rights [dumitval]
* xlwt and xlrd added to Naaya as dependencies. No need to assert availability. [dumitval]

1.4.30 (2014-01-07)
-------------------
* task 17799 - export mail list to xcel [baragdan]

1.4.29 (2013-12-18)
-------------------
class-based selection of cells with emails to be validated [dumitval]

1.4.28 (2013-12-11)
-------------------
* Email Validation - resolve validation in backend threads (avoid server load) [baragdan]

1.4.27 (2013-12-10)
-------------------
* added option to skip paragraph splitting [dumitval]

1.4.26 (2013-12-09)
-------------------
* Email Validation - controll js parallelism (avoid server load) [baragdan]

1.4.25 (2013-12-05)
-------------------
* Added email validation [baragdan]

1.4.24 (2013-11-19)
-------------------
* archive sent invitation mails + listing and individual view [dumitval]
* testfix admin_comments [dumitval]

1.4.23 (2013-11-04)
-------------------
* added export of own comments for normal users [dumitval]

1.4.22 (2013-07-26)
-------------------
* removed duplicated notification to maintainer [dumitval]

1.4.21 (2013-02-27)
-------------------
* #4595 - send invitation on behalf of
1.4.20 (2012-12-11)
-------------------
* comments are no longer subject of approval [simiamih]

1.4.19 (2012-11-28)
-------------------
* bugfix: #10085: removed misleading prompt when leaving comments [mihaitab]

1.4.18 (2012-11-22)
-------------------
* backwards compatibility: simplejson as json [mihaitab]

1.4.17 (2012-11-20)
-------------------
* (#10022) Improve comments summary. Add comments trend chart [mihaitab]

1.4.16 (2012-11-20)
-------------------
* (#10022) Improve comments summary [mihaitab]

1.4.15 (2012-11-20)
-------------------
* bugfix: #10002; write Byte Order Marker for the exported CSV [nituacor]

1.4.14 (2012-11-20)
-------------------
* ugly temporary quickfix for flickering scrollbar of iframe [simiamih]
* add "replies" column to comments tables [moregale]

1.4.13 (2012-08-16)
-------------------
* Added permission to comment/reply after consultation deadline [dumitval]

1.4.12 (2012-08-08)
-------------------
* bugfix: close comment window link for anonymous [simiamih]

1.4.11 (2012-07-13)
-------------------
* #964 - redesigned comment edit/delete permissions [simiamih]

1.4.10 (2012-07-04)
-------------------
* adapted to correctly create footnote links [dumitval]
* fixed deprecation warning (bad super addressing) [simiamih]
* fixed tests: invitees comments do not need aproval [simiamih]

1.4.9 (2012-03-23)
------------------
* Removed approval workflow for comments [dumitval]

1.4.8 (2012-03-14)
------------------
* feature: bulk send invitations [simiamih]
* fixed permission for "Manage comments" button [simiamih]

1.4.7 (2012-02-21)
------------------
* Added confirmation dialog when closing an unsubmitted comment window [dumitval]

1.4.6 (2012-01-19)
------------------
* bugfix: iframe resize in IE9 [simiamih]

1.4.5 (2012-01-06)
------------------
* Bugfix for editing a comment [dumitval]

1.4.4 (2011-11-14)
------------------
* permission information update [andredor]

1.4.3 (2011-11-04)
------------------
* update script for consultations without invitations [andredor]
