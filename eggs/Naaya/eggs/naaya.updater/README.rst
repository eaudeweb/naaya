Naaya updater
=============
Update tool for naaya sites.

How it works
------------
This package will add at start-up a new node in ZODB in the root of your
Zope instance called naaya_updates (Within ZMI navigate to
Root folder > naaya_updates). Here you'll find a list of update scripts. These
are actually zope3 utility components registered trough zcml (see configure.zcml)
in this package.

Update scripts (utilities)
--------------------------
Update scripts are utilities that provides interface IUpdateScript from this
package. You can write your own utility from scratch or you can reuse the API
provided in this package

    >>> from Products.naayaUpdater.updates import UpdateScript
    >>> class MyUpdateScript(UpdateScript):
    ...     title = 'Update portal title'
    ...     authors = ['John Doe']
    ...     creation_date = 'Jan 01, 2010'
    ...     def _update(self, portal):
    ...         self.log.info("Updating title for %r", portal)
    ...         portal.title = 'Portal new title'
    ...         return True

Optionally you can set the following script properties:
    - description
    - priority

Now all you have to do is to register this script as utility. Within your
package configure.zcml:

    <configure
      xmlns="http://namespaces.zope.org/zope"
      xmlns:zcml="http://namespaces.zope.org/zcml"
      i18n_domain="naaya">

      <configure zcml:condition="installed Products.naayaUpdater">
        <utility
          name="a-new-script.update"
          provides="Products.naayaUpdater.interfaces.IUpdateScript"
          component="my.package.updates.my_update_script.MyUpdateScript"
          permission="zope2.ViewManagementScreens" />
      </configure>

    </configure>


Major code changes that require update scripts
----------------------------------------------
The listing starts from revision `14301`. Previous updates are not
covered.

r14484
    ExtJs removed in favour of jQuery. The `Update jQuery` script
    makes sure the correct version of jQuery is included.

r14557
    Big refactoring of ``GeoMapTool``. Run the update `Update properties
    of portal_map`. Also check that the `portal_map` default view looks
    right (it might have changed coordinates or zoom level).

r14640
    Schema widgets don't inherit from ``LocalPropertyManager`` anymore.
    The update script `Convert schema widget titles to string` will fix up
    their properties, otherwise widget labels (the ``title`` property)
    will not show correct values.
