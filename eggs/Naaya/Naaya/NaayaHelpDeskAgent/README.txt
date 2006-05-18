README for HelpDeskAgent Product

   HelpDeskAgent is a product to successfully track and respond
   to ticket HelpDesk issues. Documentation of relevant cases is
   kept into archives and it is easy accessible by performing
   searches using various filters.

How to use it

   First you install HelpDeskAgent.tgz in the Products folder and restart
   Zope. You will now be able to create objects of the type "HelpDesk".
   The form will ask you for:

    - Id and Title: object's id and title

    - User Folder: needed to create HelpDesk users

    - Mail server name and port: needed to send email notifications

    - Add Issue Email Subject

    - Update Issue Email Subject

    - Delete Issue Email Subject

    - Add Issue Comment Email Subject

    - Update Issue Comment Email Subject

    - Delete Issue Comment Email Subject

    - Issue ticket length: there is a default value of 15 (digits)
  
   Second, go to 'Administration' tab to set up some thing for the
   product to work properly:

    - 'Settings' - here you can edit all the information you entered
    when you added the product

    - 'Catalog' - here you can update the HelpDesk catalog. It does this
    by deleting all indexes and re-cataloging all currently indexed issues

    - 'Priority' - here you can define priorities; each priority has a
    title, a description and a value

    - 'Status' - here you can define statuses for the issues; each status
    has a title, a description and an order.  When an issue is created
    the default status is the one with the smallest order value

    - 'Categories' - here you can define categories of issues; each
    category has a title, a description, a default priority an implicit
    advice for this type of issues and a link where the user can find
    also informations for this type of issues

    - 'Users' - here you can create HelpDesk users. A HelpDesk
    user is linked with users from specified UserFolder or from a
    LDAPUserFolder. Each user has a name, an email address and a local
    role (Issue Administrator and/or Issue Resolver)

  In the HelpDesk product folder is a file named 'HelpDesk.ini'. Before
  you add the product you can define here some default data to be added
  to the product(priority, status, sendtype and category).

  For example:
      IssuePriority=101,low,,0

    This line tells that a priority will be created with : id = '101',
    title = 'low', description = '', value = 0

After you set up all this information, the 'HelpDeskAgent' can
be used. All you have to do is to a link in your site to point the
'index_html' from your 'HelpDesk' object.

