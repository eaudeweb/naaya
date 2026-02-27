"""
Lightweight browser views to serve yafowil widget JS/CSS resources
for the pas.plugins.ldap management page.

The standard yafowil.plone resource views depend on Plone (CMFPlone,
plone.registry) which is not available in Naaya. These views serve
the essential JS and CSS directly from the yafowil egg files on disk.
"""
import os

from Products.Five import BrowserView


def _find_egg_resource(egg_prefix, rel_path):
    """Find a resource file inside an egg directory."""
    import sys
    for path_entry in sys.path:
        if os.path.basename(path_entry).startswith(egg_prefix):
            full = os.path.join(path_entry, rel_path)
            if os.path.isfile(full):
                return full
    return None


# Bootstrap Icons inline CSS for the 4 icons used by yafowil widgets.
# Using inline SVG data URIs to avoid needing the full bootstrap-icons font.
_BOOTSTRAP_ICONS_CSS = r"""
.bi-plus-circle-fill,
.bi-dash-circle-fill,
.bi-arrow-up-circle-fill,
.bi-arrow-down-circle-fill {
    display: inline-block;
    width: 1em;
    height: 1em;
    vertical-align: -0.125em;
    background-size: contain;
    background-repeat: no-repeat;
    background-position: center;
}
.bi-plus-circle-fill {
    background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' fill='%230d6efd' viewBox='0 0 16 16'%3E%3Cpath d='M16 8A8 8 0 1 1 0 8a8 8 0 0 1 16 0zM8.5 4.5a.5.5 0 0 0-1 0v3h-3a.5.5 0 0 0 0 1h3v3a.5.5 0 0 0 1 0v-3h3a.5.5 0 0 0 0-1h-3v-3z'/%3E%3C/svg%3E");
}
.bi-dash-circle-fill {
    background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' fill='%230d6efd' viewBox='0 0 16 16'%3E%3Cpath d='M16 8A8 8 0 1 1 0 8a8 8 0 0 1 16 0zM4.5 7.5a.5.5 0 0 0 0 1h7a.5.5 0 0 0 0-1h-7z'/%3E%3C/svg%3E");
}
.bi-arrow-up-circle-fill {
    background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' fill='%230d6efd' viewBox='0 0 16 16'%3E%3Cpath d='M16 8A8 8 0 1 0 0 8a8 8 0 0 0 16 0zm-7.5 3.5a.5.5 0 0 1-1 0V5.707L5.354 7.854a.5.5 0 1 1-.708-.708l3-3a.5.5 0 0 1 .708 0l3 3a.5.5 0 0 1-.708.708L8.5 5.707V11.5z'/%3E%3C/svg%3E");
}
.bi-arrow-down-circle-fill {
    background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' fill='%230d6efd' viewBox='0 0 16 16'%3E%3Cpath d='M16 8A8 8 0 1 1 0 8a8 8 0 0 1 16 0zM8.5 4.5a.5.5 0 0 0-1 0v5.793L5.354 8.146a.5.5 0 1 0-.708.708l3 3a.5.5 0 0 0 .708 0l3-3a.5.5 0 0 0-.708-.708L8.5 10.293V4.5z'/%3E%3C/svg%3E");
}
"""


class YafowilJS(BrowserView):
    """Serve concatenated yafowil widget JavaScript."""

    def __call__(self):
        self.request.response.setHeader('Content-Type',
                                        'application/javascript')
        parts = []
        # Array widget JS (must load before dict widget)
        path = _find_egg_resource(
            'yafowil.widget.array',
            'yafowil/widget/array/resources/bootstrap5/widget.js')
        if path:
            with open(path, 'r') as f:
                parts.append('/* yafowil.widget.array */\n')
                parts.append(f.read())

        # Dict widget JS
        path = _find_egg_resource(
            'yafowil.widget.dict',
            'yafowil/widget/dict/resources/bootstrap5/widget.js')
        if path:
            with open(path, 'r') as f:
                parts.append('\n/* yafowil.widget.dict */\n')
                parts.append(f.read())

        return '\n'.join(parts)


class YafowilCSS(BrowserView):
    """Serve concatenated yafowil widget CSS."""

    def __call__(self):
        self.request.response.setHeader('Content-Type', 'text/css')
        parts = []

        # Bootstrap Icons (inline SVG for the 4 icons used)
        parts.append('/* Bootstrap Icons (subset) */\n')
        parts.append(_BOOTSTRAP_ICONS_CSS)

        # Array widget CSS
        path = _find_egg_resource(
            'yafowil.widget.array',
            'yafowil/widget/array/resources/bootstrap5/widget.min.css')
        if path:
            with open(path, 'r') as f:
                parts.append('\n/* yafowil.widget.array */\n')
                parts.append(f.read())

        # Dict widget CSS
        path = _find_egg_resource(
            'yafowil.widget.dict',
            'yafowil/widget/dict/resources/bootstrap5/widget.min.css')
        if path:
            with open(path, 'r') as f:
                parts.append('\n/* yafowil.widget.dict */\n')
                parts.append(f.read())

        return '\n'.join(parts)
