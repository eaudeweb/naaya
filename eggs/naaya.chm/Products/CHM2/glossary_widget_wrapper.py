"""
This patch takes the output of GlossaryWidget.glossary_tree and marks certain
words as bold. Those words are selected which are only found in a single term.
Also, for the `chm_nl` portal, it passes the glossary's title through the
translation tool.
"""

import re
import logging
import simplejson as json

log = logging.getLogger(__name__)

def patch_glossary_widget():
    from Products.NaayaCore.SchemaTool.widgets.GlossaryWidget import \
            GlossaryWidget

    if getattr(GlossaryWidget.glossary_tree, '_bold_words_patch', False):
        log.debug("GlossaryWidget.glossary_tree already patched")
        return # already patched

    log.debug("patching GlossaryWidget.glossary_tree")
    GlossaryWidget._glossary_tree_before_bold_words_patch = GlossaryWidget.glossary_tree
    glossary_tree_wrapper._bold_words_patch = True
    GlossaryWidget.glossary_tree = glossary_tree_wrapper

def glossary_tree_wrapper(widget, REQUEST, lang='en', **kw):
    """ patched GlossaryWidget.glossary_tree """

    old_meethod = widget._glossary_tree_before_bold_words_patch
    tree_json = old_meethod(REQUEST, lang=lang, **kw)

    if widget.getId() != 'chm_terms-property':
        # we're only interested in patching output of the chm_terms widget
        return tree_json

    glossary = widget.get_glossary()
    if glossary is None: # no glossary configured; return original response.
        return tree_json

    try:
        bold_map = {}
        language_name = glossary.get_language_by_code(lang)
        for word in words_to_bold(glossary, language_name):
            bold_map[word] = re.compile(r'\b'+re.escape(word)+r'\b',
                                        re.IGNORECASE)

        tree = json.loads(tree_json)

        # skip the top node because it's the glossary itself
        for sub_tree in tree['children']:
            bold_words_in_tree(sub_tree, bold_map)

        # chm_nl - translate the title
        portal = widget.getSite()
        if widget.getPhysicalPath()[1] == 'chm_nl':
            translate = portal.getPortalTranslations()
            tree['data']['title'] = translate(tree['data']['title'])

        tree_json = json.dumps(tree)

    except:
        # Something bad happened. Log it and return the original response.
        widget.getSite().log_current_error()

    return tree_json


def bold_words_in_tree(tree, bold_map):
    """ walk `tree`, search for any words in `bold_map`, and make them bold """

    for sub_tree in tree['children']:
        bold_words_in_tree(sub_tree, bold_map)

    title = tree['data']['title']

    if 'glossary-translation-missing' in title:
        pass # translation is from another language; nothing to bold here.

    else:
        for word, word_pattern in bold_map.iteritems():
            title = word_pattern.sub('<b>%s</b>' % word, title)

        tree['data']['title'] = title

def words_to_bold(glossary, lang_name):
    out = []
    textindex = glossary.GlossaryCatalog._catalog.indexes[lang_name].index
    wid_to_word = textindex._lexicon._wids
    wid_to_docid = textindex._storage._wid2doc
    for wid in wid_to_word:
        count = len(wid_to_docid[wid])
        if count == 1:
            word = wid_to_word[wid][0]
            out.append(word)
    return out
