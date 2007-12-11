# Python imports
from os.path import join, dirname, abspath

def getCompressedJavaScript(languages=[], themes=[], plugins=[],
                            customFiles=[], suffix=""):
    """Packs the TinyMCE core, languages, themes, plugins and the custom files
       in a single string.

	The purpose of this function is to minimize the number of HTTP requests.

        @param languages: languages used by TinyMCE
        @param themes: themes used by TinyMCE
        @param plugins: plusings used by TinyMCE
        @param customFiles: custom files used along with TinyMCE
        @param suffix: "" or "_src" when using debug versions
    """
    # calculate list of files
    # TODO for Python 2.4: switch to iterator comprehension
    files = ['tiny_mce'+suffix+'.js']
    files += [join('langs', lang+'.js') for lang in languages]
    files += [join('themes', theme, 'editor_template'+suffix+'.js') \
                for theme in themes]
    for plugin in plugins:
        base = join('plugins', plugin)
        files.append(join(base, 'editor_plugin'+suffix+'.js'))
        files += [join('langs', lang+'.js') for lang in languages]
    files += customFiles
    # concatenate files
    tiny_mce_dir = join(dirname(__file__), 'tinymce', 'jscripts', 'tiny_mce')
    content = ['tinyMCE_GZ.end();'] # patch loading functions
    for name in files:
        # security check: verify that the file is under the TinyMCE
        # directory to event reading other unrelated files
        # (e.g. "/etc/passwd")
        name = abspath(join(tiny_mce_dir, name))
        if not name.startswith(tiny_mce_dir):
            raise RuntimeError('File is not under the TinyMCE directory')
        f = open(name)
        content.append(f.read())
        f.close()
    content.append('tinyMCE_GZ.end();') # restore loading functions
    content = "".join(content)
    return content
