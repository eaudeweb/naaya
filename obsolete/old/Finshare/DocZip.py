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
# Agency (EEA).  Portions created by Finsiel Romania are
# Copyright (C) European Environment Agency. All
# Rights Reserved.
#
# Author(s):
# Alexandru Ghica - Finsiel Romania

#Python imports
import os
import time
import tempfile
from zipfile import *
from os.path import join 

#Zope imports
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo

#Product imports
from Products.Finshare.Constants import *
from Products.Finshare.DocFile import addDocFile, manage_addDocFile_html


class DocZip:
    """."""

    def __init__(self):
        """ constructor """
        pass

    security = ClassSecurityInfo()
    security.setDefaultAccess("allow")

    security.declareProtected(PERMISSION_ADD_DOC_FILE, 'addDocFile')
    addDocFile = addDocFile

    security.declareProtected(PERMISSION_ADD_DOC_FILE, 'manage_addDocFile_html')
    manage_addDocFile_html = manage_addDocFile_html


    #######################
    #   ZIP FUNCTIONS     #
    #######################

    def __objectsTree(self, p_ids_list):
        """ return the objects tree """
        l_ids_list = []
        l_ids_list.append(self)
        l_ids_list.extend(p_ids_list)
        l_obs = self.__generateTree(l_ids_list)
        return l_obs

    def __generateTree(self, p_ob):
        """ recursively creats the objects tree """
        l_results = []
        l_results.append(p_ob[0])
        for l_ob in p_ob[1:]:
            if l_ob.meta_type == METATYPE_DMFILE:
                l_results.append(l_ob)
            if l_ob.meta_type in [METATYPE_DMFOLDER, METATYPE_DMARTICLE]:
                l_child_objs=[]
                l_all_childs = []
                l_child_objs.append(l_ob)
                l_child_objs.extend(l_ob.objectValues([METATYPE_DMFILE, METATYPE_DMFOLDER, METATYPE_DMARTICLE]))
                l_all_childs.extend(self.__generateTree(l_child_objs))
                l_results.append(l_all_childs)
        return l_results

    def __getTreeToZip(self, p_zf, p_list, p_path):
        """ creats the ZIP archive based on objects tree """
        l_size = 0
        l_path = p_path + p_list[0].title_or_id() + '/'
        for l_ob in p_list[1:]:
            if type(l_ob) != type([]):
                l_size = l_size + float(l_ob.get_size())
                timetuple = time.localtime()[:6]
                zfi = ZipInfo(l_path + l_ob.downloadfilename)
                zfi.date_time = timetuple
                zfi.compress_type = ZIP_DEFLATED
                p_zf.writestr(zfi, str(l_ob.data))
            else:
                l_child_size = self.__getTreeToZip(p_zf, l_ob, l_path)
                l_size = l_size + l_child_size
        return l_size

    def zip_generator(self, download_ids, p_info='', RESPONSE=None):
        """ zip all the requested objects """
        path = join(DOCMANAGER_VAR_PATH, self.getDocManagerUID())
        l_download_ids = self.utSplitToList(download_ids)
        tempfile.tempdir = path
        tmpfile = tempfile.mktemp(".temp")

         #theoretically creates an empty directory, 48 or 16 for external_attr
#        timetuple = time.localtime()[:6]
#        zfi = ZipInfo('download/', timetuple)
#        zfi.external_attr = 48
#        l_zf.writestr(zfi, '')

        l_starting_objs = self.getObjectsByIds(l_download_ids)
        l_filetree = self.__objectsTree(l_starting_objs)

        l_zf = ZipFile(tmpfile,"w")
        l_zf_info = self.__getTreeToZip(l_zf, l_filetree, '')
        l_zf.close()
        stat = os.stat(tmpfile)

        if p_info==1:
            os.unlink(tmpfile)
            return (self.getSize(l_zf_info), self.getSize(stat[6]))

        l_file = open(tmpfile, 'rb')
        content = l_file.read()
        l_file.close()
        os.unlink(tmpfile)

        RESPONSE.setHeader('Content-Type', 'application/x-zip')
        RESPONSE.setHeader('Content-Disposition', 'attachment; filename=%s' % ZIP_DOWNLOAD_FILENAME)
        RESPONSE.setHeader('Content-Length', stat[6])
        return content


    #########################
    #   UNZIP FUNCTIONS     #
    #########################

    def __addFilesFromZip(self, p_zipfile, p_name):
        """ Generate title and id for DMFiles and add them into DocManager"""
        from string import rfind
        l_title = p_name[max(rfind(p_name,'/'),
                     rfind(p_name,'\\'),
                     rfind(p_name,':')
                    )+1:]
        l_id = 'file' + self.utGenRandomId(6)
        self.addDocFile(id=l_id, title=l_title, downloadfilename=l_title, file=p_zipfile.read())

    def manage_addZipFile(self, file=''):
        """ Expand a zipfile into a number of Documents.
            Go through the zipfile and for each file in there call
            self.manage_addProduct['Report Document'].manageaddDocument(id,...
        """
        try:
            if type(file) is not type('') and hasattr(file,'filename'):
                # According to the zipfile.py ZipFile just needs a file-like object
                zf = ZZipFile(file)
                for name in zf.namelist():
                    # test that the archive is not hierarhical
                    if name[-1] == '/' or name[-1] == '\\':
                        return (ZIP_HIERARCHICAL, 'err')

                for name in zf.namelist():
                    zf.setcurrentfile(name)
                    self.__addFilesFromZip(zf,name)
                return (ZIP_CREATED, 'ok')
            else:
                return (ZIP_VALID_FILE, 'err')
        except:
            return (ZIP_VALID_FILE, 'err')

InitializeClass(DocZip)


# Support class to provide more similarity with Zope upload files.
# Sometimes the calling program will make a read() with a maxsize.
# This class will simply deliver what is available even if it is bigger.
# On some occasions though, the size of the content will be exactly the
# amount request and the calling function will assume that there is more
# to read. Therefore we allow only one read to work.

class ZZipFile(ZipFile):

    def read(self,size=-1):
        """ """
        if(self.hasbeenread == 0):
            self.hasbeenread = 1
            return ZipFile.read(self,self.filename)
        else:
            return ""

    def seek(self):
        """ Ignore since it is only used to figure out size """
        self.hasbeenread = 0
        return 0

    def tell(self):
        """ """
        return self.getinfo(filename).file_size

    def setcurrentfile(self,filename):
        """ """
        self.hasbeenread = 0
        self.filename=filename