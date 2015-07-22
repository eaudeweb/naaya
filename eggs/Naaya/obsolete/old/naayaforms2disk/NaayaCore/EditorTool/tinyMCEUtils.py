# Python imports
from os.path import join, dirname, abspath

TINYMCE_DIR = join(dirname(__file__), 'tinymce', 'jscripts', 'tiny_mce')

def getCompressedJavaScript(isJS=False, languages=[], themes=[], plugins=[],
                            customFiles=[], suffix=""):
    """Packs the TinyMCE code in a single string.

        The core, the languages, the themes, the plugins and the custom files
        are included. The purpose of this function is to minimize the number
        of HTTP requests.

        @param isJS: ??? (see TinyMCE docs) TODO
        @param languages: languages used by TinyMCE
        @param themes: themes used by TinyMCE
        @param plugins: plugins used by TinyMCE
        @param customFiles: custom files used along with TinyMCE
        @param suffix: "" or "_src" when using debug versions
    """
    # Inspired by the .NET and PHP TinyMCE compressors

    if not isJS:
        return getFileContent('tiny_mce_gzip.js') + 'tinyMCE_GZ.init({});'

    # calculate list of files
    # TODO for Python 2.4: switch to iterator comprehension
    files = []
    files += [join('langs', lang+'.js') for lang in languages]
    for theme in themes:
        base = join('themes', theme)
        files.append(join(base, 'editor_template'+suffix+'.js'))
        files += [join(base, 'langs', lang+'.js') for lang in languages]
    for plugin in plugins:
        base = join('plugins', plugin)
        files.append(join(base, 'editor_plugin'+suffix+'.js'))
        files += [join(base, 'langs', lang+'.js') for lang in languages]
    files += customFiles
    # concatenate files
    content = []
    content.append(getFileContent('tiny_mce'+suffix+'.js'))
    content.append('tinyMCE_GZ.start();') # patch loading functions
    for name in files:
        content.append(getFileContent(name))
    content.append('tinyMCE_GZ.end();') # restore loading functions
    content = "".join(content)
    return content

def getFileContent(name):
    """Return the contents of the file from the TinyMCE directory"""
    # security check: verify that the file is under the TinyMCE
    # directory to prevent reading other unrelated files, e.g. "/etc/passwd"
    name = abspath(join(TINYMCE_DIR, name))
    if not name.startswith(TINYMCE_DIR):
        raise RuntimeError('File is not under the TinyMCE directory')
    f = open(name)
    content = f.read()
    f.close()
    return content
