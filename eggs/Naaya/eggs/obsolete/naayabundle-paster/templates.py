from paste.script.templates import Template, var
from paste.util.template import paste_script_template_renderer

class NaayaBundleTemplate(Template):
    """A paster script template for creating naaya bundles."""

    _template_dir = 'bundle-template'
    summary = 'Create a bundle'
    vars = [
        var('version', 'Version', default='0.1'),
        var('description', 'One-line description', default='Naaya bundle'),
        var('long_description', 'Multi-line description (in reST)'),
        var('keywords', 'Space-separated keywords', default='naaya bundle'),
        var('author', 'Author name', default='Eau de Web'),
        var('author_email', 'Author email', default='office@eaudeweb.ro'),
        var('url', 'URL', default='http://naaya.eaudeweb.ro/'),
        var('license_name', 'License name', default='MPL'),
        var('parent', 'Parent naaya bundle. Ex: Naaya, CHM, Groupware',
            default='Naaya')
    ]
    template_renderer = staticmethod(paste_script_template_renderer)
