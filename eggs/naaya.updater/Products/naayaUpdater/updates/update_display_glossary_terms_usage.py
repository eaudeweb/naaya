from Products.naayaUpdater.updates import UpdateScript
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import view_management_screens
import traceback

# this is for compatibility with older versions of Zope (< 2.9)
try:
    import transaction
    begin_transaction = transaction.begin
    get_transaction = transaction.get
except:
    begin_transaction = get_transaction().begin

class UpdateDisplayGlossaryUsage(UpdateScript):
    """
    Generic script that returns a list with all customised indexes of folders
    """

    title = 'Display glossary terms usage, remove terms in invalid languages'
    authors = ['Valentin Dumitru']
    creation_date = 'Oct 17, 2011'
    description = 'Displays a usage count for terms in the glossary_coverage'

    security = ClassSecurityInfo()

    security.declareProtected(view_management_screens, 'manage_update')
    def manage_update(self, REQUEST):
        """ perform this update """
        report_html = ''
        portals = {}
        if REQUEST.REQUEST_METHOD == 'POST':
            do_dry_run = (REQUEST.form.get('action') != 'Run update')
            global_terms = {}
            for portal_path in REQUEST.form.get("portal_paths", []):
                portal = self.unrestrictedTraverse(portal_path)
                success, log_data, global_terms = self.update(portal,
                        do_dry_run, global_terms)

                report_html += '<br/><br/>'
                report_html += '<h4>'+portal_path+'</h4>'
                if success:
                    report_html += '<h4>SUCCESS</h4>'
                else:
                    report_html += '<h4>FAILED</h4>'

                report_html += self.report_html
                self.report_html = ''

                report_html += html_quote(log_data)

                portals[portal_path] = success

            self._setup_logger()
            self.log_sorted_results(global_terms)
            report_html += '<br/><br/>'
            report_html += '<h4>Top terms for all portals</h4>'
            report_html += html_quote(self.log_output.getvalue())
            if not do_dry_run:
                self.add_log(self.id, portals,
                             self.REQUEST.AUTHENTICATED_USER.getUserName())

        return self.update_template(REQUEST, report=report_html,
                                    form=REQUEST.form)

    security.declareProtected(view_management_screens, 'update')
    def update(self, portal, do_dry_run, global_terms):
        self._setup_logger()
        begin_transaction()
        transaction = get_transaction()
        try:
            success, global_terms = self._update(portal, global_terms)

            transaction.note('Update "%s" on Naaya site "%s"' %
                (self.id, portal.absolute_url(1)))

            if do_dry_run:
                transaction.abort()
            else:
                transaction.commit()

        except Exception, e:
            self.log.error('Update script failed - "%s"' % str(e))
            self.log.error(traceback.format_exc())
            transaction.abort()
            success = False

        log_data = self.log_output.getvalue()
        return success, log_data, global_terms
    def _update(self, portal, global_terms):
        global_terms = self.display_glossary_usage(portal, global_terms)
        return True, global_terms

    def display_glossary_usage(self, portal, global_terms):
        """ Returns an ordered list with terms from the glossary
        and the count of their usage in objects """
        objects = portal.getCatalogedObjectsCheckView(meta_type=['Naaya Folder',
            'Naaya Photo Folder', 'Naaya Photo Gallery', 'Naaya Contact',
            'Naaya Survey', 'Naaya Educational Product', 'Naaya News',
            'Naaya Story', 'Naaya File', 'Naaya URL', 'Naaya Extended File',
            'Naaya Document', 'Naaya Event', 'Naaya Media File', 'Naaya Pointer',
            'Naaya Blob File', 'Naaya Localized Blob File', 'Naaya GeoPoint'])
        terms = {}
        language_mapping = {}
        processed_languages = []
        glossary = getattr(portal, 'glossary_keywords')
        for object in objects:
            ob_terms = set()
            terms_all_langs = object._local_properties.get('keywords')
            if terms_all_langs:
                for lang in terms_all_langs.keys():
                    ln_terms = terms_all_langs[lang][0].split(',') 
                    ln_terms = [term.strip() for term in ln_terms if term.strip()]
                    if lang not in object.gl_get_languages():
                        properties = object._local_properties.copy()
                        self.log.debug('%s keyword in language %s deleted from %s' % (terms_all_langs[lang], lang, object.absolute_url()))
                        del(properties['keywords'][lang])
                        object._local_properties = properties
                        break
                    elif lang not in processed_languages:
                        language_mapping.update(self.get_language_mapping(
                            glossary, lang))
                        processed_languages.append(lang)
                    ln_terms = self.translate_terms(language_mapping, ln_terms)
                    ob_terms.update(ln_terms)
                for term in ob_terms:
                    if term in terms.keys():
                        terms[term] += 1
                    else:
                        terms[term] = 1
                    if term in global_terms.keys():
                        global_terms[term] += 1
                    else:
                        global_terms[term] = 1
        self.log_sorted_results(terms)

        return global_terms

    def get_language_mapping(self, glossary, lang):
        gl_catalog = glossary.getGlossaryCatalog()
        gl_terms = []
        for brain in gl_catalog({}):
            try:
                ob = brain.getObject()
                if ob.meta_type == 'Naaya Glossary':
                    self.log.error('%s present in the glossary catalog' % ob.getId())
                else:
                    gl_terms.append(brain.getObject())
            except KeyError:
                pass
        language = glossary.get_language_by_code(lang)
        language_mapping = {}
        for term in gl_terms:
            term_ln = term.get_translation_by_language(language)
            term_en = term.get_translation_by_language('English')
            language_mapping[term_ln.lower()] = term_en
        return language_mapping

    def translate_terms(self, language_mapping, ln_terms):
        translated = []
        for term in ln_terms:
            if term:
                translated.append(language_mapping.get(term.lower(), term))
        return translated

    def log_sorted_results(self, terms):
        if terms:
            count = 0
            terms_tuples = [(term_tuple[1], term_tuple[0])
                    for term_tuple in terms.items()]
            terms_tuples.sort(reverse=True)
            for term in terms_tuples:
                count += 1
                self.log.debug('%s. %s: %s' % (count, term[1], term[0]))

def html_quote(v):
    return v.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

