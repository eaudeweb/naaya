from datetime import date, timedelta

from Products.Naaya.tests.NaayaFunctionalTestCase import NaayaFunctionalTestCase
from Products.Naaya.NyFolder import addNyFolder
from Products.NaayaSurvey.MegaSurvey import manage_addMegaSurvey
from Products.NaayaCore.EmailTool.EmailTool import divert_mail
import transaction
from pyquery import PyQuery


class WidgetFunctionalTest(NaayaFunctionalTestCase):
    def setUp(self):
        super(WidgetFunctionalTest, self).setUp()

        self.portal.gl_add_site_language('fr', 'French')
        addNyFolder(self.portal, 'myfolder', contributor='admin', submitted=1)
        releasedate = (date.today() - timedelta(days=1)).strftime('%d/%m/%Y')
        expirationdate = (date.today() + timedelta(days=10)).strftime('%d/%m/%Y')
        manage_addMegaSurvey(self.portal.myfolder, title="Test survey",
            releasedate=releasedate, expirationdate=expirationdate,
            allow_anonymous=0, contributor='admin', submitted=0)
        self.survey = self.portal.myfolder['test-survey']
        self.diverted_mail = divert_mail()
        self.survey_url = 'http://localhost/portal/myfolder/test-survey'
        transaction.commit()

    def tearDown(self):
        divert_mail(False)
        self.portal.manage_delObjects(['myfolder'])
        transaction.commit()

    def test_radio_missing_language(self):
        self.browser_do_login('admin', '')
        self.browser.go(self.survey_url)
        pq = PyQuery(self.browser.get_html())
        goto_edit_questions_page = pq('div.buttons>a:contains("Edit Questions")')
        self.assertTrue(goto_edit_questions_page)
        goto_edit_questions_page = goto_edit_questions_page[0]
        self.assertTrue(goto_edit_questions_page.attrib.get('href'))
        self.browser.go(goto_edit_questions_page.attrib['href'])

        # Change language to other than english (default)
        pq = PyQuery(self.browser.get_html())
        # Why is the name of the link 'fr' instead of 'French' as set above?
        lang_url = pq("div#language>a:contains('fr')")
        self.assertTrue(lang_url)
        lang_url = lang_url[0].attrib.get("href")
        self.assertTrue(lang_url)
        self.browser.go(lang_url)
        self.browser.go(goto_edit_questions_page.attrib['href'])

        # Add radio question
        form = self.browser.get_form('frmAdd')
        self.assertTrue(form.find_control('title'))
        self.assertTrue(form.find_control('meta_type'))

        expected_title = 'Radio Question ...'

        form['title'] = expected_title
        self.browser.clicked(form, form.find_control('title'))
        form['meta_type'] = ['Naaya Radio Widget']
        self.browser.clicked(form, form.find_control('meta_type'))
        self.browser.submit()

        # Go to question preview page
        pq = PyQuery(self.browser.get_html())
        questions = pq("table#folderfile_list td.title-column")
        self.assertTrue(questions)
        question = questions[0]
        self.assertTrue(expected_title in question.text_content())
        question_links = [ q for q in question.iterlinks()]
        self.assertTrue(question_links)
        self.assertTrue(question_links[0][2])
        self.browser.go(question_links[0][2])

        # Go to Edit question
        pq = PyQuery(self.browser.get_html())
        goto_edit = pq("div#admin_this_folder a")
        self.assertTrue(len(goto_edit) > 0)
        goto_edit = goto_edit[0].attrib.get('href')
        self.assertTrue(goto_edit)
        self.browser.go(goto_edit)

        # Edit the question
        pq = PyQuery(self.browser.get_html())
        current_lang = pq("div.translate div.current")
        self.assertTrue('French' in current_lang[0].text_content())

        form = self.browser.get_form('frmEdit')
        self.assertTrue(form)
        self.assertEqual(form['title'], expected_title)
        expected_tooltips = 'fr text'
        form['tooltips'] = expected_tooltips
        self.browser.clicked(form, form.find_control('tooltips'))
        expected_choices = 'fr opt1\nfr opt2\n'
        form['choices:lines'] = expected_choices
        self.browser.clicked(form, form.find_control('choices:lines'))
        self.browser.submit()

        # Change the language
        current_lang = pq("div.translate a")
        self.browser.go(current_lang[0].attrib['href'])

        # Check the helper tootips
        pq = PyQuery(self.browser.get_html())
        hz_pairs = pq("div.horizontal-pairs")
        # the formatting will differ in help tip ('fr opt1\n\t\t...')
        # so check only a part of expected text
        expected_pairs = [expected_title, expected_tooltips, 'fr opt1']
        self.assertEqual(len(hz_pairs), len(expected_pairs))
        for i, e in enumerate(expected_pairs):
            label_for = hz_pairs[i].cssselect("label")[0].attrib['for']
            inputFieldValue = hz_pairs[i].cssselect("div.field #%s" % label_for
                                )[0].attrib.get('value', '')
            helpField = hz_pairs[i].cssselect("div.tip")[0]
            self.assertEqual(inputFieldValue, '')
            self.assertTrue(e in helpField.text_content())

        # Add a value on the new language
        form = self.browser.get_form('frmEdit')
        self.assertTrue(form)
        self.assertEqual(form['title'], '')
        expected_newTitle = "en title"
        form['title'] = expected_newTitle
        self.browser.clicked(form, form.find_control('title'))
        self.browser.submit()

        # Check the tooltip is gone for the present value
        pq = PyQuery(self.browser.get_html())
        hz_pairs = pq("div.horizontal-pairs")
        for p in hz_pairs:
            label_for = p.cssselect("label")[0].attrib['for']
            helpFields = p.cssselect("div.tip")
            if label_for == 'title':
                inputFieldValue = p.cssselect("div.field #%s" % label_for
                                )[0].attrib['value']
                self.assertEqual(inputFieldValue, expected_newTitle)
                # no more help fields here
                self.assertFalse(helpFields)
            else:
                # the rest of the help fields show up
                self.assertTrue(helpFields)

