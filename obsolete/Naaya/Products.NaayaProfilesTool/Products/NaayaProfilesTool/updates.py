from Products.naayaUpdater.updates import UpdateScript
from Products.NaayaCore.ProfilesTool.ProfilesTool import (
    manage_addProfilesTool, BTreeProfilesTool)

class ProfilesToolToBTree(UpdateScript):
    title = 'Change ProfilesTool to use BTree'
    authors = ['Alex Morega']
    creation_date = 'Oct 06, 2010'

    def _update(self, portal):
        old_profiles_tool = portal.getProfilesTool()
        if isinstance(old_profiles_tool, BTreeProfilesTool):
            self.log.info('already a BTree, nothing to update')
            return True

        self.log.info('extracting profile from old container ...')
        _profiles_meta = old_profiles_tool.profiles_meta
        profiles = []
        for profile_ob in old_profiles_tool.objectValues():
            profile_ob = profile_ob.aq_base
            assert profile_ob.meta_type == 'Naaya Profile'
            old_profiles_tool._delObject(profile_ob.id)
            del profile_ob._v__object_deleted__ # just to be safe
            profiles.append(profile_ob)
        self.log.info('%r profiles', len(profiles))

        self.log.info('removing old profiles container ...')
        portal._delObject(old_profiles_tool.id)

        self.log.info('new profiles container ...')
        manage_addProfilesTool(portal)
        new_profiles_tool = portal.getProfilesTool()
        new_profiles_tool.profiles_meta = _profiles_meta

        self.log.info('saving profiles ...')
        for profile_ob in profiles:
            new_profiles_tool._setObject(profile_ob.id, profile_ob,
                                         set_owner=False)

        self.log.info('done')

        return True
