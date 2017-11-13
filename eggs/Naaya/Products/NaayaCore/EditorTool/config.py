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


from copy import deepcopy


def _filter_string(input, exclude):
    return ' '.join([p for p in input.split(' ') if p != exclude])


def _no_image(config):
    config = deepcopy(config)

    config['plugins'] = _filter_string(config['plugins'], 'advimage')

    config['insert_button_items'] = _filter_string(
        config['insert_button_items'], 'image')

    config['menu']['insert']['items'] = _filter_string(
        config['menu']['insert']['items'], 'image')

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
            'items': 'undo redo | cut copy paste pastetext | '
                     'selectall searchreplace'
        },
        'insert': {
            'title': 'Insert',
            'items': 'media image link | charmap hr anchor pagebreak '
                     'insertdatetime nonbreaking template toc'
        },
        'view': {
            'title': 'View',
            'items': 'visualchars visualblocks visualaid | '
                     'preview fullscreen help'
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
            'items': 'code'
        },
    },

    'menubar': 'edit insert view format table tools',

    'insert_button_items': 'media image link | charmap hr anchor pagebreak '
                           'insertdatetime nonbreaking template toc',

    'toolbar1': 'preview searchreplace | undo redo | insert | '
                'bullist numlist outdent indent | '
                'visualblocks code fullscreen help',
    'toolbar2': 'styleselect | fontselect | fontsizeselect | '
                'bold italic underline  | '
                'alignleft aligncenter alignright alignjustify | '
                'forecolor backcolor | removeformat',

    'fontsize_formats': '8pt 10pt 11pt 12pt 14pt 18pt 24pt 36pt',

    'style_formats': [
        {
            'title': 'Box',
            'block': 'div',
            'classes': 'box'
        },
    ],
    'style_formats_merge': True,

    'plugins': 'compat3x advlist autolink lists advlink advimage charmap print'
               ' preview hr anchor pagebreak searchreplace wordcount '
               'visualblocks visualchars code fullscreen code insertdatetime '
               'media nonbreaking table contextmenu directionality '
               'template paste textcolor colorpicker textpattern '
               'codesample toc help emoticons hr'
}

SECTIONS = {
    'tinymce': _DEFAULT,
    'tinymce_noimage': _no_image(_DEFAULT),
}
