"""
Inspector View shows information about the site bundles.
It registers for INySite.
"""

from zope.component import getGlobalSiteManager, queryMultiAdapter
from Products.Five.browser import BrowserView

from interfaces import IDiff, IBundleReloader

class InspectorView(BrowserView):
    # site manager related functions
    def _managers(self):
        gsm = getGlobalSiteManager()
        manager = self.context.getSiteManager()
        while True:
            yield manager
            if manager is gsm:
                break
            manager = manager.__bases__[0]

    def get_managers(self):
        return list(self._managers())

    def get_manager_name(self, manager):
        return getattr(manager, '__name__', None)

    def get_manager_class_name(self, manager):
        return manager.__class__.__name__

    # interface related functions
    def get_interfaces(self):
        interfaces = set()
        for manager in self._managers():
            for utility in manager.registeredUtilities():
                interfaces.add(utility.provided)
        return sorted(interfaces)

    def get_interface_name(self, interface):
        return getattr(interface, '__name__', None)

    def get_interface_by_name(self, interface_name):
        for interface in self.get_interfaces():
            if interface_name == self.get_interface_name(interface):
                return interface
        return None

    # utility related functions
    def get_utilities_names(self, interface):
        names = set()
        manager = self.context.getSiteManager()
        for name, utility in manager.getUtilitiesFor(interface):
            names.add(name)
        return sorted(names)

    def get_utility_registrations(self, interface, name):
        utility_registrations = []
        for manager in self._managers():
            for utility in manager.registeredUtilities():
                if (utility.provided == interface
                        and utility.name == name):
                    utility_registrations.append(utility)

        return utility_registrations

    def has_utility(self, manager, utility_registrations):
        """ check if an utility is in that specific manager """
        registries = [ui.registry for ui in utility_registrations]
        return manager in registries

    def can_get_diff(self, utility_registrations):
        if len(utility_registrations) < 2:
            return False
        for ur1, ur2 in zip(utility_registrations[1:], utility_registrations):
            if queryMultiAdapter((ur1.component, ur2.component), IDiff):
                return True
        return False

    def is_reloader_available(self, bundle_name):
        gsm = getGlobalSiteManager()
        reloader = gsm.queryUtility(IBundleReloader, name=bundle_name)
        return (reloader is not None)


class InspectorDiffView(InspectorView):
    def get_diffs(self, utility_registrations):
        if len(utility_registrations) < 2:
            return []

        ret = []
        for ur1, ur2 in zip(utility_registrations[1:], utility_registrations):
            diff = queryMultiAdapter((ur1.component, ur2.component, ), IDiff)
            if diff is not None:
                ret.append({
                    'manager1': ur1.registry,
                    'manager2': ur2.registry,
                    'html_diff': diff.html_diff,
                    })
        return ret


class InspectorReloadView(InspectorView):
    def __call__(self):
        gsm = getGlobalSiteManager()
        bundle_name = self.request.form['bundle_name']
        reloader = gsm.queryUtility(IBundleReloader, name=bundle_name)
        reloader.reload_bundle()
        self.request.RESPONSE.redirect('inspector_view')
