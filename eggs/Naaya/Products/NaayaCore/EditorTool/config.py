from copy import deepcopy

# Configuration file for the EditorTool. This files contains two (default) or
# more (your own) templates. In templates you can customize appearance and
# functionality of tinymce.
# For a list of TinyMCE parameters
# see: https://www.tinymce.com/docs/configure/integration-and-setup/

# Also there are four Naaya specific parameters:
# img_popup_w - Width of the image upload plugin in pixels
# img_popup_h - Height of the image upload plugin in pixels
# link_popup_w - Width of the link plugin in pixels
# link_popup_h - Height of the link plugin in pixels


def _no_image(config):
    config = deepcopy(config)
    config['plugins'] = ' '.join([
        p for p in config['plugins'].split(' ')
        if p != 'advimage'
    ])
    return config


_DEFAULT = {
    'img_popup_w': 900,
    'img_popup_h': 500,
    'link_popup_w': 470,
    'link_popup_h': 450,
    'width': '70%',
    'height': '20ex',
    'extended_valid_elements': '*[*],a[id|name|href|target|title|onclick|rel]',
    'remove_trailing_brs': False,
    'relative_urls': False,
    'convert_urls': True,

    'menu': {
        'edit': {
            'title': 'Edit',
            'items': 'undo redo | cut copy paste pastetext | selectall'
        },
        'insert': {
            'title': 'Insert',
            'items': 'advlink advimage media | template hr'
        },
        'view': {
            'title': 'View',
            'items': 'visualaid'
        },
        'format': {
            'title': 'Format',
            'items': 'bold italic underline strikethrough superscript '
                     'subscript | formats | removeformat'
        },
        'table': {
            'title': 'Table',
            'items': 'inserttable tableprops deletetable | cell row column'
        },
        'tools': {
            'title': 'Tools',
            'items': 'spellchecker code'
        },
    },

    'toolbar1': 'advlink advimage preview searchreplace | undo redo | insert | '
                'bullist numlist outdent indent | '
                'visualblocks code fullscreen help',
    'toolbar2': 'styleselect | fontselect | fontsizeselect | '
                'bold italic underline  | '
                'alignleft aligncenter alignright alignjustify | '
                'forecolor backcolor | removeformat',

    'style_formats': [
        {'title': 'Box', 'classes': 'box'},
    ],
    'style_formats_merge': True,

    'plugins': 'compat3x advlist autolink lists advlink advimage charmap print '
               'preview hr anchor pagebreak searchreplace wordcount '
               'visualblocks visualchars code fullscreen code insertdatetime '
               'media nonbreaking save table contextmenu directionality '
               'template paste textcolor colorpicker textpattern imagetools '
               'codesample toc help emoticons hr'
}

SECTIONS = {
    'tinymce': _DEFAULT,
    'tinymce_noimage': _no_image(_DEFAULT),
}