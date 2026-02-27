import os
import time
import tempfile
from StringIO import StringIO
from zipfile import ZipFile
from os.path import join

from Products.SEMIDE.constants import ZIP_DOWNLOAD_FILENAME
from Products.NaayaBase.constants import MESSAGE_SAVEDCHANGES
from Products.NaayaPhotoArchive.constants import METATYPE_NYPHOTO
from Products.NaayaPhotoArchive.NyPhoto import addNyPhoto

class SemideZip(object):
    """ """
    #######################
    #   ZIP FUNCTIONS     #
    #######################

    def __objectsTree(self, p_ids_list):
        #return the objects tree
        l_ids_list = []
        l_ids_list.append(self)
        l_ids_list.extend(p_ids_list)
        l_obs = self.__generateTree(l_ids_list)
        return l_obs

    def __generateTree(self, p_ob):
        #recursively creats the objects tree
        l_results = []
        l_results.append(p_ob[0])
        for l_ob in p_ob[1:]:
            if l_ob.meta_type in self.get_ziped_metatypes():
                l_results.append(l_ob)
            if l_ob.meta_type in self.get_containers_metatypes():
                l_child_objs=[]
                l_all_childs = []
                l_child_objs.append(l_ob)
                l_child_objs.extend(l_ob.objectValues(self.get_downloadable_metatypes()))
                l_all_childs.extend(self.__generateTree(l_child_objs))
                l_results.append(l_all_childs)
        return l_results

    def __getTreeToZip(self, p_zf, p_list, p_path):
        #creats the ZIP archive based on objects tree
        l_size = 0
        l_path = p_path + self.utToUtf8(p_list[0].id) + '/'
        for l_ob in p_list[1:]:
            if type(l_ob) != type([]):
                l_size = l_size + float(l_ob.get_size())
                timetuple = time.localtime()[:6]
                if l_ob.meta_type != METATYPE_NYPHOTO:
                    filename = l_path + self.utToUtf8(l_ob.id)
                else:
                    extension = l_ob.content_type.split("/")[1]
                    filename = l_path + self.utToUtf8(l_ob.id) + "." + extension
                zfi = ZipInfo(filename)
                zfi.date_time = timetuple
                zfi.compress_type = ZIP_DEFLATED
                if l_ob.meta_type == METATYPE_NYFILE:
                    p_zf.writestr(zfi, str(l_ob.get_data()))
                elif l_ob.meta_type == METATYPE_NYPHOTO:
                    p_zf.writestr(zfi, str(l_ob.get_data()))
                else:
                    p_zf.writestr(zfi, str(l_ob.getFileItem().get_data()))
            else:
                l_child_size = self.__getTreeToZip(p_zf, l_ob, l_path)
                l_size = l_size + l_child_size
        return l_size

    def zip_generator(self, download_ids, fld_url='', p_info='', zip_file_name=ZIP_DOWNLOAD_FILENAME, RESPONSE=None):
        """ zip all the requested objects """
        path = join(CLIENT_HOME, self.getSite().id)
        context = self.getDownloadContext(fld_url)
        if not os.path.isdir(path):
            try:
                os.mkdir(path)
            except:
                raise OSError, 'Can\'t create directory %s' % path

        l_download_ids = self.splitToList(download_ids, '/')
        tempfile.tempdir = path
        tmpfile = tempfile.mktemp(".temp")

        l_starting_objs = context.getObjectsByIds(l_download_ids)
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

        RESPONSE.setHeader('Content-Type', 'application/x-zip-compressed')
        RESPONSE.setHeader('Content-Disposition', 'attachment; filename=%s' % zip_file_name)
        RESPONSE.setHeader('Content-Length', stat[6])
        return content

    #########################
    #   UNZIP FUNCTIONS     #
    #########################

    def isValidImage(self, file):
        from PIL import Image
        from cStringIO import StringIO
        try:
            Image.open(StringIO(file))
            return True
        except IOError: # Python Imaging Library doesn't recognize it as an image
            return False

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
