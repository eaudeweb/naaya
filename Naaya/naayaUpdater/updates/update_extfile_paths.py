# The contents of this file are subject to the Mozilla Public
# License Version 1.1 (the "License"); you may not use this file
# except in compliance with the License. You may obtain a copy of
# the License at http://www.mozilla.org/MPL/
#
# Software distributed under the License is distributed on an "AS
# IS" basis, WITHOUT WARRANTY OF ANY KIND, either express or
# implied. See the License for the specific language governing
# rights and limitations under the License.
#
# The Initial Owner of the Original Code is European Environment
# Agency (EEA).  Portions created by Eau de Web are
# Copyright (C) European Environment Agency.  All
# Rights Reserved.
#
# Authors:
#
# Alex Morega, Eau de Web

import os

from Products.naayaUpdater.updates import nyUpdateLogger as logger
from Products.naayaUpdater.NaayaContentUpdater import NaayaContentUpdater
from Products.ExtFile.ExtFile import ExtFile
from Products.NaayaBase.NyFSFile import NyFSFile

def extfile_path(extfile):
    return extfile._get_fsname(extfile.filename)

class CustomContentUpdater(NaayaContentUpdater):
    """ Change ExtFile filesystem paths """
    def __init__(self, id):
        NaayaContentUpdater.__init__(self, id)
        self.title = 'Update ExtFile folders layout'
        self.description = 'Change ExtFile folders layout from SLICED_HASH to SYNC_ZODB'
        self.update_meta_type = [
            'Naaya File',
            'Naaya Extended File',
            'Naaya Media File',
            'Naaya Photo',
        ]

    def _verify_doc(self, doc):
        """ Check for ExtFile path format """
        if list(self._list_updatable_extfiles(doc)):
            return doc
        else:
            return None

    def _update(self):
        """ Iterate over all files in need of updating """
        renamer = ExtFileRenamer(skip_missing=True)

        try:
            for ob in self._list_updates():
                for extfile in self._list_updatable_extfiles(ob):
                    renamer.update(extfile)

        except:
            try:
                renamer.rollback()
            except:
                logger.debug("Update ExtFile paths: error while cleaning up failed update!")
            raise

        else:
            renamer.commit()

        renamer.log_missing()

    def _list_updatable_extfiles(self, ob):
        """ List all ExtFile instances that need updating """
        if ob.meta_type == 'Naaya File':
            all_extfiles = self._list_NyFile_updatable_extfiles(ob)
        elif ob.meta_type == 'Naaya Extended File':
            all_extfiles = self._list_NyExFile_updatable_extfiles(ob)
        elif ob.meta_type == 'Naaya Media File':
            all_extfiles = self._list_NyMediaFile_updatable_extfiles(ob)
        elif ob.meta_type == 'Naaya Photo':
            all_extfiles = self._list_NyPhoto_updatable_extfiles(ob)
        else:
            raise ValueError('Unexpected content type')

        for extfile in all_extfiles:
            filename = extfile.filename
            if len(filename) == 3 and len(filename[0]) == 1 and len(filename[1]) == 1:
                # this looks like a hashed filename. It's not 100% accurate, but good enough
                yield extfile

    def _list_NyFile_updatable_extfiles(self, ob):
        """ Update NyFile objects """
        # update the main file
        yield ob._ext_file

        # update older versions
        for version in ob.versions.objectValues('ExtFile'):
            yield version

    def _list_NyExFile_updatable_extfiles(self, ob):
        """ Update NyFile objects """
        for lang in ob.objectValues():
            if isinstance(lang, NyFSFile):
                yield lang._ext_file
                # TODO: lang.versions
                for version in lang.versions.objectValues('ExtFile'):
                    yield version

        # don't update any checked-out versions because they don't
        # copy extfile instances properly (the filesystem file is shared)

    def _list_NyMediaFile_updatable_extfiles(self, ob):
        """ Update NyMediaFile objects """
        for fsfile in ob.objectValues('ExtFile'):
            yield fsfile

    def _list_NyPhoto_updatable_extfiles(self, ob):
        """ Update NyPhoto objects """
        for fsfile in ob.objectValues('ExtFile'):
            yield fsfile

class ExtFileRenamer(object):
    def __init__(self, dry_run=False, skip_missing=False):
        self.old_files = []
        self.new_files = []
        self.missing_files = []
        self.dry_run = dry_run
        self.skip_missing_files = skip_missing

    def update(self, extfile):
        try:
            old_fsname = extfile._fsname(extfile.filename)
            new_filename = extfile._get_new_ufn()
            new_fsname = extfile._fsname(new_filename)

            if os.path.isfile(old_fsname):
                pass
            elif os.path.isfile(old_fsname + '.undo'):
                old_fsname += '.undo'
            elif os.path.isfile(old_fsname + '.tmp'):
                old_fsname += '.tmp'
            else:
                if not self.skip_missing_files:
                    raise ValueError("Missing filesystem file for ExtFile object (%s)" % old_fsname)
                self.missing_files.append(old_fsname)

            logger.debug("Update ExtFile paths: copying \"%s\" to \"%s\"", old_fsname, new_fsname)
            if not self.dry_run:
                self.copy(old_fsname, new_fsname)
                extfile.filename = new_filename

            self.old_files.append(old_fsname)
            self.new_files.append(new_fsname)

        finally:
            extfile._dir__unlock()

    def copy(self, src, dst):
        try:
            # avoid copying - do a filesystem hard link (only works on unix)
            import os.link
            os.link(src, dst)
        except:
            # we can't hardlink; do a copy instead
            import shutil
            shutil.copyfile(src, dst)

    def log_missing(self):
        for missing_file in self.missing_files:
            logger.debug("Update ExtFile paths: missing file \"%s\"", missing_file)

    def rollback(self):
        logger.debug("Update ExtFile paths: an error occurred; rolling back changes")
        for f in self.new_files:
            logger.debug("Update ExtFile paths: removing \"%s\"", f)
            if not self.dry_run:
                os.unlink(f)

    def commit(self):
        logger.debug("Update ExtFile paths: operation successful; cleaning up old files")
        for f in self.old_files:
            logger.debug("Update ExtFile paths: removing \"%s\"", f)
            if not self.dry_run:
                os.unlink(f)

def register(uid):
    return CustomContentUpdater(uid)
