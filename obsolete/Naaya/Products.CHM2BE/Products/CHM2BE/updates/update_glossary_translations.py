from zipfile import ZipFile
import simplejson as json
import lxml.etree
from cStringIO import StringIO

from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import view_management_screens
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Globals import InitializeClass

from naaya.core.utils import force_to_unicode
from Products.naayaUpdater.updates import UpdateScript

class UpdateGlossaryTranslations(UpdateScript):
    title = 'Update Glossary translations'
    authors = ['Andrei Laza']
    creation_date = 'Nov 24, 2011'
    security = ClassSecurityInfo()

    def lang_names(self, ob):
        ret = {}
        for lang_info in ob.get_languages_list():
            lang_code = lang_info['lang']
            lang_name = lang_info['english_name']
            ret[lang_code] = lang_name
        return ret

    def get_translations(self, node):
        ret = {}
        for e in node.xpath('./translation'):
            ret[e.attrib['lang']] = e.text
        return ret

    def set_translation(self, ob, translation, lang, lang_attr, method_name):
        if not translation:
            return
        old_translation = getattr(ob.aq_base, lang_attr, u'')
        if old_translation:
            return
        set_method = getattr(ob, method_name)
        set_method(lang, translation)
        self.log.debug('%s - %s: from %r to %r', ob.getId(), lang_attr,
                                                 old_translation, translation)

    def set_translations(self, node, ob, languages):
        lang_names = self.lang_names(ob)

        name_node = node.xpath('./name')[0]
        name_translations = self.get_translations(name_node)
        for lang in languages:
            lang_name = lang_names[lang]
            translation = name_translations.get(lang, u'')
            translation = force_to_unicode(translation)
            self.set_translation(ob, translation, lang_name,
                                 lang_name, 'set_translations_list')

        definition_node = node.xpath('./definition')[0]
        definition_translations = self.get_translations(definition_node)
        for lang in languages:
            lang_name = lang_names[lang]
            def_lang = ob.definition_lang(lang_name)
            translation = definition_translations.get(lang, u'')
            translation = force_to_unicode(translation)
            self.set_translation(ob, translation, lang_name,
                                 def_lang, 'set_def_trans_list')

    def _update(self, portal):
        if not 'dump_file' in self.REQUEST.form:
            return False
        if not 'languages' in self.REQUEST.form:
            return False
        if not 'glossary' in self.REQUEST.form:
            return False

        dump_file = self.REQUEST.form['dump_file']
        languages = self.REQUEST.form['languages']
        glossary_name = self.REQUEST.form['glossary']
        dump_zip = ZipFile(dump_file, 'r')

        metadata = json.loads(dump_zip.read('glossary/metadata.json'))
        translations_xml = dump_zip.read('glossary/translations.xml')

        xml_dump = lxml.etree.parse(StringIO(translations_xml))
        glossary = portal._getOb(glossary_name)

        for folder_node in xml_dump.xpath('/glossary/folder'):
            folder_id = folder_node.attrib['id']
            folder = glossary._getOb(folder_id, None)
            if folder is None:
                self.log.warning("can't find folder with id %s", folder_id)
                continue

            self.set_translations(folder_node, folder, languages)

            for element_node in folder_node.xpath('./element'):
                element_id = element_node.attrib['id']
                element = folder._getOb(element_id, None)
                if element is None:
                    self.log.warning("can't find element %s in folder %s",
                            element_id, folder_id)
                    continue

                self.set_translations(element_node, element, languages)

        return True

    security.declareProtected(view_management_screens, 'standard_update_template')
    standard_update_template = UpdateScript.update_template

    security.declareProtected(view_management_screens, 'update_template')
    update_template = PageTemplateFile('zpt/update_glossary_translations', globals())
InitializeClass(UpdateGlossaryTranslations)
