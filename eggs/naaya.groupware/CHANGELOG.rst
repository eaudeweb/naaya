1.2.11 (unreleased)
-------------------

1.2.10 (2012-06-07)
-------------------
* eionet forum index uses text settings for messages [simiamih]
* #885 - using 3 level cutoff for subscriptions in profile_overview [simiamih]
* improved headings in profile overview [bogdatan]

1.2.9 (2012-06-06)
------------------
* Improved profile overview to show only the IGs that account is
  explicitly assigned [bogdatan]

1.2.8 (2012-05-23)
------------------
* using port when connecting to ldap in member_search [simiamih]
* fixed test for profileoverview [simiamih]

1.2.7 (2012-05-22)
------------------
* custom interface for SINAnet instance [simiamih]
* profileoverview: also use port when creating ldap connection [simiamih]

1.2.6 (2012-05-15)
------------------
* explanatory text for ig membership request [dumitval]

1.2.5 (2012-05-14)
-------------------
* member_search now searches in both uid and full name [dumitval]

1.2.4 (2012-05-10)
-------------------
* refactored profile overview, subscriptions on callback [simiamih]

1.2.3 (2012-05-04)
-------------------
* using ny_ldap_group_roles meta in catalog *update* [simiamih]

1.2.2 (2012-04-27)
-------------------
* bugfix: AttributeError: generate_csv [nituacor]

1.2.1 (2012-04-17)
-------------------
* delete button for nyfolders [simiamih]

1.2.0 (2012-04-13)
-------------------
* Created a JSON view to return all portals from 
  archives.eionet.europa.eu for forum.eionet.europa.eu [bogdatan]

1.1.22 (2012-04-12)
-------------------
* customizable instance titles and welcome text [simiamih]

1.1.21 (2012-04-10)
-------------------
* Fixed NFP Admin Link to be called only for nfp-eionet website [bogdatan]
* Fixed profile overview to get local roles for specified user [bogdatan]

1.1.20 (2012-04-04)
-------------------
* Changed from search.eionet.europa.eu/search.jsp to Google Search [bogdatan]
* Updated administration portlet with comments management section
  and API keys status section [bogdatan]

1.1.19 (2012-03-16)
-------------------
* fixed zope 2.12 merging GET and POST in review_ig_request [simiamih]
* fixed tests: index_html is now simpleView [simiamih]

1.1.18 (2012-03-15)
-------------------
* added nofollow to zip download links [dumitval]

1.1.17 (2012-02-23)
-------------------
* fixed js for IE - profileoverview [bogdatan]

1.1.16 (2012-02-22)
-------------------
* fixed sorted NameError in profileoverview index.pt [simiamih]

1.1.15 (2012-02-22)
-------------------
* nfp_nrc link is enabled in nfp-eionet [simiamih]

1.1.14 (2012-02-15)
-------------------
* using ldap cache to display all members in members search [bogdatan]

1.1.13 (2012-02-10)
-------------------
* profileoverview shows specific profile by GET for managers [bogdatan]

1.1.12 (2012-02-02)
-------------------
* updated zope_customs documentation

1.1.11 (2012-02-02)
-------------------
* changed from customized index page to simpleView [bogdatan]
* changed names in IGs listing [bogdatan]
* archived IGs list made collapsible [bogdatan]
* added 'Edit NRC members' for nfp-eionet, currently disabled
  from py until CIRCA migration [bogdatan]
* profileoverview shows local roles owned by belonging to
  a ldap group [simiamih]
* profileoverview - ajax loading ig roles + role names [simiamih]
* list all button in member search

1.1.10 (2012-01-18)
-------------------
* bugfix: decode user names used in email template [simiamih]

1.1.9 (2012-01-16)
------------------
* Added modification time to the folder listing [dumitval]

1.1.8 (2012-01-13)
------------------
* Added i18n id for translation of 'Type' [dumitval]

1.1.7 (2012-01-12)
------------------
* fix style and logos for left/right logos [simiamih]

1.1.6 (2012-01-12)
------------------
* Fix name of Groupware bundle [dumitval]

1.1.5 (2012-01-11)
------------------
* updated common styles [bulanmir]

1.1.4 (2012-01-09)
------------------
* load groupware bundle [dumitval]
* changed message on member search page [dumitval]
* filter display for User management search [andredor]
* feature: naaya.groupware.profileoverview [simiamih]

1.1.3 (2011-10-28)
------------------
* Owner can have just edit content permission (admin other properties) [andredor]
* standard templates updated to site logo changes [dumitval]

1.1.2 (2011-10-14)
------------------
* portlet administration on disk for new gw sites [andredor]
* portlet administration also on disk [andredor]
* IGWSite interface (derived from INySite) [andredor]
