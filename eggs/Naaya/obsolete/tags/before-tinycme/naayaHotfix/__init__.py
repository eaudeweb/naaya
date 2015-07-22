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
# Copyright (C) European Environment Agency.  All
# Rights Reserved.
#
# Authors:
#
# Cornel Nitu, Finsiel Romania
# Dragos Chirila, Finsiel Romania

#Python imports
from time import time
import sys
import os, popen2

#Zope imports
from zLOG import LOG, ERROR, INFO, PROBLEM, DEBUG, WARNING
from Products.PageTemplates.GlobalTranslationService import setGlobalTranslationService

#Product imports
from Products.NaayaCore.TranslationsTool.TranslationsTool import TranslationsTool
from Products.Localizer.LocalPropertyManager import LocalPropertyManager

from Products.Localizer.MessageCatalog import MessageCatalog
from itools.resources import memory
from itools.handlers import PO
from Globals import PersistentMapping

#patch for MessageCatalog
def po_import(self, lang, data):
    """ """
    messages = self._messages

    resource = memory.File(data)
    po = PO.PO(resource)

    # Load the data
    for msgid in po.get_msgids():
        if isinstance(msgid, unicode):  msgid = msgid.encode('utf-8')
        if msgid:
            msgstr = po.get_msgstr(msgid) or ''
            if not messages.has_key(msgid):
                messages[msgid] = PersistentMapping()
            messages[msgid][lang] = msgstr

        # Set the encoding (the full header should be loaded XXX)
        self.update_po_header(lang, charset=po.get_encoding())

MessageCatalog.po_import = po_import

#patch for Localizer
def _setLocalPropValue(self, id, lang, value):
    # Get previous value
    old_value, timestamp = self.get_localproperty(id, lang)
    # Update value only if it is different
    if value != old_value:
        properties = self._local_properties.copy()
        if not properties.has_key(id):
            properties[id] = {}
        properties[id][lang] = (value, time())
        self._local_properties = properties

LocalPropertyManager._setLocalPropValue = _setLocalPropValue

class GlobalTranslationService:
    def translate(self, domain, msgid, *args, **kw):
        if domain == 'default':
            domain = 'portal_translations'
        context = kw.get('context')
        if context is None: return msgid
        translation_service = getattr(context, domain, None)
        if translation_service is not None:
            if isinstance(translation_service, TranslationsTool):
                return translation_service.translate(domain, msgid, *args, **kw)
        return msgid

def initialize(context):
    """ """
    setGlobalTranslationService(GlobalTranslationService())

LOG('naayaHotfix', DEBUG, 'Patch for Localizer and other stuff')

#patch for TextIndexNG2. 
import sys
from Products.TextIndexNG2.converters import doc, ppt, ps, ooffice, pdf, xls
from Products.TextIndexNG2.converters.doc import wvConf_file
from Products.TextIndexNG2.Registry import ConverterRegistry
from Products.TextIndexNG2.converters.stripogram import html2text

#patch converters/doc.py
def doc_convert(self, doc):
    """Convert WinWord document to raw text"""
    tmp_name = self.saveFile(doc)
    if sys.platform == 'win32':
        return self.execute('antiword -m UTF-8.txt "%s"' % tmp_name)
    else:
        return self.execute('wvWare -c utf-8 --nographics -x "%s" "%s" 2> /dev/null' % (wvConf_file, tmp_name))

def doc_convert2(self, doc, encoding, mimetype):
    if encoding:
        return self.convert(doc), encoding
    return self.convert(doc), 'utf-8'

doc.Converter.convert = doc_convert
doc.Converter.convert2 = doc_convert2


#patch converters/ppt.py
def ppt_convert2(self, doc, encoding, mimetype):
    if encoding:
        return self.convert(doc), encoding
    return self.convert(doc), 'iso-8859-15'
ppt.Converter.convert2 = ppt_convert2

#patch converters/ps.py
def ps_convert2(self, doc, encoding, mimetype):
    if encoding:
        return self.convert(doc), encoding
    return self.convert(doc), 'iso-8859-15'
ps.Converter.convert2 = ps_convert2

#patch converters/oo.py
def oo_convert2(self, doc, encoding, mimetype):
    if encoding:
        return self.convert(doc), encoding
    return self.convert(doc), 'utf-8'
ooffice.Converter.convert2 = oo_convert2

#patch converters/pdf.py
def pdf_convert2(self, doc, encoding, mimetype):
    """Convert pdf data to raw text"""
    tmp_name = self.saveFile(doc)
    if sys.platform == 'win32':
        html = self.execute('pdftohtml -stdout -i -noframes "%s"' % tmp_name)
        if encoding:
            return html2text(html,
                             ignore_tags=('img',),
                             indent_width=4,
                             page_width=80), encoding
        else:
            return html2text(html,
                             ignore_tags=('img',),
                             indent_width=4,
                             page_width=80), 'utf-8'
    else:
        if encoding:
            return self.execute('pdftotext -enc UTF-8 "%s" -' % tmp_name), encoding
        return self.execute('pdftotext -enc UTF-8 "%s" -' % tmp_name), 'utf-8'
pdf.Converter.convert2 = pdf_convert2

#patch converters/xls.py
def xls_convert(self, doc):
    """Convert Excel document to raw text"""
    tmp_name = self.saveFile(doc)
    if sys.platform == 'win32':
        html = self.execute('xlhtml "%s"' % tmp_name)
        return html2text(html,
                     ignore_tags=('img',),
                     indent_width=4,
                     page_width=80)
    else:
        return self.execute('xls2csv -d UTF-8 -q 0 "%s" 2> /dev/null' % tmp_name)
xls.Converter.convert = xls_convert

def xls_convert2(self, doc, encoding, mimetype):
    if encoding:
        return self.convert(doc), encoding
    return self.convert(doc), 'iso-8859-15'
xls.Converter.convert2 = xls_convert2

LOG('naayaHotfix', DEBUG, 'TextIndexNG2 patched')

depends_on = 'ppthtml'
ppt.Converter.depends_on = depends_on

cv = 'ppt'
converter = ppt.Converter()

depends_on = getattr(converter, 'depends_on', None)
if depends_on and os.name == 'posix':
    PO =  popen2.Popen3('which %s' % depends_on)
    out = PO.fromchild.read()
    PO.wait()
    del PO
    if out.find('no %s' % depends_on) > - 1 or out.lower().find('not found') > -1 or len(out.strip()) == 0:
        LOG('naayaHotfix', WARNING, 'Converter "%s" not registered because executable "%s" could not be found' % (cv, depends_on))

for t in converter.getType():
    try:
        ConverterRegistry.register(t, converter)
        LOG('naayaHotfix', INFO, 'Converter "%s" for %s registered' % (cv, t))
    except:
        LOG('naayaHotfix', INFO, 'Converter "%s" for %s NOT registered' % (cv, t))

from OFS.content_types import guess_content_type
from Products.TextIndexNG2.Registry import NormalizerRegistry
from Products.TextIndexNG2.Registry import SplitterRegistry, RegistryException
from Products.TextIndexNG2.TextIndexNG import TextIndexNG

def _index_object(self, documentId, obj, threshold=None, attr=''):

    encoding = self.default_encoding
    source = mimetype = None

    # This is to support foreign file formats that
    # are stored as "File" objects when searching
    # through PrincipiaSearchSource

    if hasattr(obj, 'txng_get'):
        # Check if the object has a method txng_get()
        result = obj.txng_get([attr])
        if result is None: return None
        source, mimetype, encoding = result

    elif obj.meta_type in ('File', 'Portal File', 'Naaya File') and  \
       attr in ('PrincipiaSearchSource', 'SearchableText'):

        source= getattr(obj, attr, None)
        if source and not self.use_converters:
            if callable(source): source = source()
        else:              
            source = str(obj)
        mimetype = obj.content_type

    elif obj.meta_type == 'ExtFile' and \
       attr in ('PrincipiaSearchSource', 'SearchableText'):
        source = obj.index_html()
        mimetype = obj.getContentType()

    elif obj.meta_type in ('ZMSFile',):
        lang = attr[attr.rfind('_')+1:]
        req = {'lang' : lang}
        file = obj.getObjProperty('file', req)
        source = ''
        mimetype = None
        if file:
            source = file.getData()
            mimetype = file.getContentType()

    elif obj.meta_type in ('TTWObject',) and attr not in ('SearchableText', ): 
        field = obj.get(attr)
        source = str(field)
        if field.meta_type in ( 'ZMSFile', 'File' ):
            mimetype = field.getContentType()
        else:
            mimetype = None

    else:
        # default behaviour: try to obtain the source from
        # the attribute or method call return value

        try:
            source = getattr(obj, attr)
            if callable(source): source = source()
            if not isinstance(source, unicode):
                source = str(source)
        except (AttributeError, TypeError):
            return None
    
    # If enabled, we try to find a valid document converter
    # and convert the data to get a hopefully text only representation
    # of the data.

    if self.use_converters:
        if mimetype is None or mimetype == 'application/octet-stream':
            mimetype, encoding = guess_content_type(obj.getId(), source)
            if not encoding:
                encoding = self.default_encoding

        try: 
            converter = ConverterRegistry.get(mimetype)
        except RegistryException: 
            LOG('textindexng', ERROR, '%s could not be converted because no converter could be found for %s' % (obj.absolute_url(1), mimetype))
            return None

        if converter:
            try:
                source, encoding = converter.convert2(source, encoding, mimetype)
            except:
                try:
                    source = converter.convert(source)
                except:
                    LOG('textindexng', ERROR, '%s could not be converted' % obj.absolute_url(1), error=sys.exc_info())
                    return None

        if obj.meta_type == 'Portal File': 
            source += ' ' + obj.SearchableText()

    # Now we try to get a valid encoding. For unicode strings
    # we have to perform no action. For string objects we check
    # if the document has an attibute (not a method) '<index>_encoding'.
    # As fallback we also check for the presence of an attribute
    # 'document_encoding'. Checking for the two attributes allows
    # us to define different encodings for different attributes
    # on an object. This is useful when an object stores multiple texts
    # as attributes within the same instance (e.g. for multilingual
    # versions of a text but with different encodings). 
    # If no encoding is specified as object attribute, we will use
    # Python's default encoding.
    # After getting the encoding, we convert the data to unicode.

    if isinstance(source, str):
        if encoding is None:
            try: encoding = self.default_encoding
            except: encoding = self.default_encoding = 'iso-8859-15'

            for k in ['document_encoding', attr + '_encoding']:
                enc = getattr(obj, k, None)
                if enc is not None: encoding = enc  

        if encoding=='ascii': encoding ='iso-8859-15'         
        try:
            source = unicode(source, encoding, 'strict')
        except UnicodeDecodeError:
            LOG('textindexng', WARNING, 'UnicodeDecodeError raised from %s - ignoring unknown unicode characters'  % obj.absolute_url(1))
            source = unicode(source, encoding, 'ignore')

    elif isinstance(source, unicode):  pass
    else: raise TXNGError,"unknown object type" 

    source = source.strip()
    if not source: return None

    # Normalization: apply translation table to data
    if self.use_normalizer:
        source = NormalizerRegistry.get(self.use_normalizer).process(source)    

    # Split the text into a list of words
    SP = SplitterRegistry.get(self.use_splitter)

    _source = source
    words = SP(casefolding  = self.splitter_casefolding,
               separator    = self.splitter_separators,
               maxlen       = self.splitter_max_len,
               singlechar   = self.splitter_single_chars
               ).split(_source)

    #  remove stopwords from data
    if self.use_stopwords:
        words = self.use_stopwords.process( words ) 

    # We pass the list of words to the corresponding lexicon
    # and obtain a list of wordIds. The "old" TextIndex iterated
    # over every single words (overhead).
    return self._lexicon.getWordIdList(words)


TextIndexNG._index_object = _index_object


#
# Patch zope pack in order to remove undo files from disk
#

#patch ExtFile
try:
    from Products.ExtFile.ExtFile import ExtFile
    extfile_installed = True
except ImportError:
    extfile_installed = False

if extfile_installed:
    from Products.ExtFile.Config import REPOSITORY_PATH
    from App.ApplicationManager import ApplicationManager
    from App.ApplicationManager import AltDatabaseManager
    from extfile_pack import pack_disk

    def am_manage_pack(self, days=0, REQUEST=None):
        """ Override manage pack in order to delete .undo files from disk."""
        # Run disk packing in separate thread
        path = os.path.join(INSTANCE_HOME, *REPOSITORY_PATH)
        pack_disk(path)
        
        t = self.__old_manage_pack(days, None)

        if REQUEST is not None:
            REQUEST['RESPONSE'].redirect(
                REQUEST['URL1']+'/manage_workspace')
        return t

    LOG('naayaHotfix', INFO, 'Patching ApplicationManager in order to delete .undo files from disk on database pack.')
    LOG('naayaHotfix', INFO, 'Patching AltDatabaseManager in order to delete .undo files from disk on database pack.')
    ApplicationManager.__old_manage_pack = ApplicationManager.manage_pack
    AltDatabaseManager.__old_manage_pack = ApplicationManager.manage_pack
    ApplicationManager.manage_pack = am_manage_pack
    AltDatabaseManager.manage_pack = am_manage_pack



    from Products.ExtFile.Config import *

    from os.path import join, isfile
    from mimetypes import guess_extension, guess_all_extensions
    import re, base64, string, sha

    copy_of_re = re.compile('(^(copy[0-9]*_of_)+)')

    def _get_new_ufn(self, path=None, content_type=None, lock=1):
        """ Create a new unique filename """
        id = self.id

        # hack so the files are not named copy_of_foo
        if COPY_OF_PROTECTION:
            match = copy_of_re.match(id)
            if match is not None:
                id = id[len(match.group(1)):]

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

        if REPOSITORY_EXTENSIONS in (MIMETYPE_APPEND, MIMETYPE_REPLACE):
            mime_ext = None
            if self.id:
                for ext in guess_all_extensions(content_type):
                    if ext == id_ext:
                        mime_ext = ext
                        break
            else:
                mime_ext = guess_extension(content_type)
            if mime_ext is None:
                mime_ext = id_ext
            if mime_ext is not None:
                if mime_ext in ('.jpeg', '.jpe'): 
                    mime_ext = '.jpg'   # for IE/Win :-(
                if mime_ext in ('.obj',):
                    mime_ext = '.exe'   # b/w compatibility
                if mime_ext in ('.tiff',):
                    mime_ext = '.tif'   # b/w compatibility
                # don't change extensions of unknown binaries
                if not (content_type == 'application/octet-stream' and id_ext):
                    if REPOSITORY_EXTENSIONS == MIMETYPE_APPEND:
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
            mkdir_exc = "Can't create directory: "
            umask = os.umask(REPOSITORY_UMASK)
            try:
                os.makedirs(dirpath)
                os.umask(umask)
            except:
                os.umask(umask)
                raise mkdir_exc, dirpath

        # generate file name
        fileformat = FILE_FORMAT
        # time/counter (%t)
        if string.find(fileformat, "%t")>=0:
            fileformat = string.replace(fileformat, "%t", "%c")
            counter = int(DateTime().strftime('%m%d%H%M%S'))
        else:
            counter = 0
        invalid_format_exc = "Invalid file format: "
        if string.find(fileformat, "%c")==-1:
            raise invalid_format_exc, FILE_FORMAT
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