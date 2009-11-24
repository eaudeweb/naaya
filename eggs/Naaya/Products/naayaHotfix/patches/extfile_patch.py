#Pyhton imports
import os

#Zope imports
from zLOG import LOG, ERROR, INFO, PROBLEM, DEBUG, WARNING


def patch_fs_paths_and_pack():
    try:
        from Products.ExtFile.ExtFile import ExtFile
        extfile_installed = True
    except ImportError:
        extfile_installed = False

    if extfile_installed:
        # configure ExtFile to generate paths based on the ZODB physical path of objects
        from Products.ExtFile import ExtFile as ExtFile_module, configuration as ExtFileConfig
        ExtFile_module.REPOSITORY = ExtFileConfig.REPOSITORY = ExtFileConfig.SYNC_ZODB
        ExtFile_module.ZODB_PATH = ExtFileConfig.ZODB_PATH = ExtFileConfig.PHYSICAL

        from Products.ExtFile.configuration import config
        from App.ApplicationManager import ApplicationManager
        from App.ApplicationManager import AltDatabaseManager
        from AccessControl.requestmethod import postonly
        from extfile_pack import pack_disk

        @postonly
        def am_manage_pack(self, days=0, REQUEST=None):
            """ Override manage pack in order to delete .undo files from disk."""
            # Run disk packing in separate thread
            path = os.path.join(INSTANCE_HOME, *config.location)
            pack_disk(path)

            t = self.__old_manage_pack(days, None)

            if REQUEST is not None:
                REQUEST['RESPONSE'].redirect(
                    REQUEST['URL1']+'/manage_workspace')
            return t

        # XXX This method is bugous
        #LOG('naayaHotfix', INFO, 'Patching ApplicationManager in order to delete .undo files from disk on database pack.')
        #LOG('naayaHotfix', INFO, 'Patching AltDatabaseManager in order to delete .undo files from disk on database pack.')
        #ApplicationManager.__old_manage_pack = ApplicationManager.manage_pack
        #AltDatabaseManager.__old_manage_pack = ApplicationManager.manage_pack.im_func
        #ApplicationManager.manage_pack = am_manage_pack
        #AltDatabaseManager.manage_pack = am_manage_pack

def patch_extfile_extension():
    # Patch _get_new_ufn
    from os.path import join, isfile
    from mimetypes import guess_extension, guess_all_extensions
    import re, base64, string, sha
    from Products.ExtFile.ExtFile import ExtFile
    from Products.ExtFile.configuration import config
    from Products.ExtFile.configuration import REPOSITORY_EXTENSIONS,\
                                               COPY_OF_PROTECTION,\
                                               MIMETYPE_APPEND,\
                                               MIMETYPE_REPLACE,\
                                               REPOSITORY,\
                                               SYNC_ZODB,\
                                               SLICED,\
                                               SLICED_REVERSE,\
                                               SLICED_HASH,\
                                               SLICE_WIDTH,\
                                               SLICE_DEPTH,\
                                               CUSTOM,\
                                               CUSTOM_METHOD,\
                                               NORMALIZE_CASE,\
                                               NORMALIZE,\
                                               REPOSITORY_UMASK,\
                                               FILE_FORMAT

    copy_of_re = re.compile('(^(copy[0-9]*_of_)+)')

    def _get_new_ufn(self, path=None, content_type=None, lock=1):
        """ Create a new unique filename """
        id = self._get_zodb_id()

        # hack so the files are not named copy_of_foo
        if COPY_OF_PROTECTION:
            id = copy_of_protect(id)

        # get name and extension components from id
        pos = string.rfind(id, '.')
        if (pos+1):
            id_name = id[:pos]
            id_ext = id[pos:]
        else:
            id_name = id
            id_ext = ''

        if not content_type:
            content_type = self.content_type

        if REPOSITORY_EXTENSIONS in (MIMETYPE_APPEND, MIMETYPE_REPLACE) and not id_ext:
            mime_ext = guess_extension(content_type)
            if mime_ext is not None:
                # don't change extensions of unknown binaries and text files
                if not (content_type in config.unknown_types and id_ext):
                    if REPOSITORY_EXTENSIONS == MIMETYPE_APPEND:
                        # don't append the same extension twice
                        if id_ext != mime_ext:
                            id_name = id_name + id_ext
                    id_ext = mime_ext

        # generate directory structure
        if path is not None:
            rel_url_list = path
        else:
            rel_url_list = self._get_zodb_path()

        dirs = []
        if REPOSITORY == SYNC_ZODB:
            dirs = rel_url_list
        elif REPOSITORY in (SLICED, SLICED_REVERSE, SLICED_HASH):
            if REPOSITORY == SLICED_HASH:
                # increase distribution by including the path in the hash
                hashed = ''.join(list(rel_url_list)+[id_name])
                temp = base64.encodestring(sha.new(hashed).digest())[:-1]
                temp = temp.replace('/', '_')
                temp = temp.replace('+', '_')
            elif REPOSITORY == SLICED_REVERSE:
                temp = list(id_name)
                temp.reverse()
                temp = ''.join(temp)
            else:
                temp = id_name
            for i in range(SLICE_DEPTH):
                if len(temp)<SLICE_WIDTH*(SLICE_DEPTH-i):
                    dirs.append(SLICE_WIDTH*'_')
                else:
                    dirs.append(temp[:SLICE_WIDTH])
                    temp=temp[SLICE_WIDTH:]
        elif REPOSITORY == CUSTOM:
            method = aq_acquire(self, CUSTOM_METHOD)
            dirs = method(rel_url_list, id)

        if NORMALIZE_CASE == NORMALIZE:
            dirs = [d.lower() for d in dirs]

        # make directories
        dirpath = self._fsname(dirs)
        if not os.path.isdir(dirpath):
            umask = os.umask(REPOSITORY_UMASK)
            try:
                os.makedirs(dirpath)
            finally:
                os.umask(umask)

        # generate file name
        fileformat = FILE_FORMAT
        # time/counter (%t)
        if string.find(fileformat, "%t")>=0:
            fileformat = string.replace(fileformat, "%t", "%c")
            counter = int(DateTime().strftime('%m%d%H%M%S'))
        else:
            counter = 0
        if string.find(fileformat, "%c")==-1:
            raise ValueError("Invalid file format '%s'" % FILE_FORMAT)
        # user (%u)
        if string.find(fileformat, "%u")>=0:
            if (getattr(self, 'REQUEST', None) is not None and
               self.REQUEST.has_key('AUTHENTICATED_USER')):
                user = getSecurityManager().getUser().getUserName()
                fileformat = string.replace(fileformat, "%u", user)
            else:
                fileformat = string.replace(fileformat, "%u", "")
        # path (%p)
        if string.find(fileformat, "%p")>=0:
            temp = string.joinfields(rel_url_list, "_")
            fileformat = string.replace(fileformat, "%p", temp)
        # file and extension (%n and %e)
        if string.find(fileformat,"%n")>=0 or string.find(fileformat,"%e")>=0:
            fileformat = string.replace(fileformat, "%n", id_name)
            fileformat = string.replace(fileformat, "%e", id_ext)

        # lock the directory
        if lock: self._dir__lock(dirpath)

        # search for unique filename
        if counter:
            fn = join(dirpath, string.replace(fileformat, "%c", ".%s" % counter))
        else:
            fn = join(dirpath, string.replace(fileformat, "%c", ''))
        while isfile(fn) or isfile(fn+'.undo') or isfile(fn+'.tmp'):
            counter = counter + 1
            fn = join(dirpath, string.replace(fileformat, "%c", ".%s" % counter))
        if counter:
            fileformat = string.replace(fileformat, "%c", ".%s" % counter)
        else:
            fileformat = string.replace(fileformat, "%c", '')

        dirs.append(fileformat)
        return dirs

    ExtFile._get_new_ufn = _get_new_ufn
    LOG('naayaHotfix', DEBUG, 'Patch for ExtFile')
