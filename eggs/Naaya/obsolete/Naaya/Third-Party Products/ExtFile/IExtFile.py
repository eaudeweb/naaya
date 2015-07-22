#
# IExtFile and IExtImage public interfaces
#

try: 
    from Interface import Interface
except ImportError:
    # Zope < 2.6
    from Interface import Base as Interface


class IExtFile(Interface):
    '''ExtFile public interface'''

    def index_html(icon=0, preview=0, width=None, height=None, REQUEST=None):
        '''The default view. Returns the file's contents.'''

    def view_image_or_file():
        '''Redirects to the default view of the file or image.'''
    
    def link(text='', **args):
        '''Returns an HTML link tag for the file or image.'''

    def is_broken():
        '''Returns true if the file does not exist in the repository, false otherwise.'''

    def get_size():
        '''Returns the size of the file or image.'''

    def size():
        '''Returns a formatted, stringified version of the file size.'''

    def get_filename():
        '''Returns the filesystem path of the file.'''

    def getContentType():
        '''Returns the file's content type (MIME type).'''

    def static_mode():
        '''Returns true if EXTFILE_STATIC_PATH is set, false otherwise.'''

    def static_url():
        '''Returns the Zope or static URL of a file, depending on static_mode().'''

    def icon_gif():
        '''Redirects to the icon for the file's MIME type.'''

    def icon_tag():
        '''Returns an HTML image tag for the icon.'''

    def getIconPath():
        '''Returns the filesystem path of the icon for the file's MIME type.'''

    def manage_editExtFile(title='', descr='', REQUEST=None):
        '''Changes the properties.'''

    def manage_upload(file='', content_type='', REQUEST=None):
        '''Uploads a file from a file handle or string buffer.'''

    def manage_file_upload(file='', content_type='', REQUEST=None):
        '''Uploads a file from a file handle or local directory.'''

    def manage_http_upload(url, REQUEST=None):
        '''Uploads a file from an HTTP server.'''

    def manage_afterUpdate(filename, content_type, size):
        '''Called whenever the file data has been updated.'''

    def PrincipiaSearchSource():
        '''Returns the contents of text/* files, empty string otherwise.'''


class IExtImage(IExtFile):
    '''ExtImage public interface'''

    def tag(preview=0, icon=0, height=None, width=None, alt=None,
            scale=0, xscale=0, yscale=0, border='0', REQUEST=None, **args):
        '''Returns an HTML image tag for this image.'''

    def width():
        '''Returns the pixel width of the main image.'''

    def height():
        '''Returns the pixle height of the main image.'''

    def format():
        '''Returns the PIL file format of the image.'''
    
    def is_webviewable():
        '''Returns true if the file format is GIF, JPEG, or PNG; false otherwise.'''

    def preview():
        '''Redirects to the preview image.'''

    def preview_tag():
        '''Returns an HTML image tag for the preview image.'''

    def get_prev_size():
        '''Returns the size of the preview image.'''

    def prev_size():
        '''Returns a formatted stringified version of the preview image size.'''

    def prev_width():
        '''Returns the pixel width of the preview image.'''

    def prev_height():
        '''Returns the pixel height of the preview image.'''

    def get_prev_filename():
        '''Returns the filesystem path of the preview image.'''

    def manage_create_prev(maxx=0, maxy=0, ratio=0, REQUEST=None):
        '''Create the preview from the main image.'''

    def manage_del_prev(REQUEST=None):
        '''Deletes the preview image.'''

    def manage_upload(file='', content_type='', is_preview=0, create_prev=0, 
                      maxx='', maxy='', ratio=0, REQUEST=None):
        '''Uploads an image or preview from a file handle or string buffer.'''

    def manage_file_upload(file='', content_type='', is_preview=0, create_prev=0,
                           maxx='', maxy='', ratio=0, REQUEST=None):
        '''Uploads an image or preview from a file handle or local directory.'''

    def manage_http_upload(url, is_preview=0, REQUEST=None):
        '''Uploads an image or preview from an HTTP server.'''

