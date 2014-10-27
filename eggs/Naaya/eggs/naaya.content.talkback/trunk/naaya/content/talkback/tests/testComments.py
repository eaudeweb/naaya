from datetime import date, timedelta
from xml.dom import minidom

from webob import Request
import transaction
from Products.Naaya.tests.NaayaTestCase import NaayaTestCase
from Products.Naaya.NyFolder import addNyFolder
from naaya.content.talkback.tbconsultation_item import addNyTalkBackConsultation
from naaya.content.talkback.comment_item import addComment
from naaya.core.zope2util import dt2DT, DT2dt

class CommentsFeedTest(NaayaTestCase):
    def setUp(self):
        super(CommentsFeedTest, self).setUp()
        addNyFolder(self.portal, 'myfolder', contributor='admin', submitted=1)
        myfolder = self.portal['myfolder']

        start_date = (date.today() - timedelta(days=1)).strftime('%d/%m/%Y')
        end_date = (date.today() + timedelta(days=10)).strftime('%d/%m/%Y')

        tb_id = addNyTalkBackConsultation(myfolder,
                title="Test consultation", contributor='admin', submitted=1,
                start_date=start_date, end_date=end_date)
        self.tb = myfolder[tb_id]

        self.tb.addSection(title="Sec", body="<p>para 1</p><p>para 2</p>")
        self.tb_url = 'http://nohost/portal/myfolder/test-consultation'

    def test_empty_feed(self):
        tb_atom_url = self.tb_url + '/comments_atom'

        doc = self.tb.comments_atom()
        assert doc.startswith('<?xml version="1.0" encoding="utf-8"?>')
        assert '<feed xmlns="http://www.w3.org/2005/Atom">' in doc
        dom = minidom.parseString(doc)
        assert dom.documentElement.tagName == 'feed'

        title = dom.getElementsByTagName('title')[0]
        assert title.firstChild.data == self.tb.title

        links = dom.getElementsByTagName('link')

        link0 = links[0].attributes
        assert sorted(link0.keys()) == ['href', 'rel']
        assert link0['rel'].value == 'self'
        assert link0['href'].value == tb_atom_url

        link1 = links[1].attributes
        assert sorted(link1.keys()) == ['href']
        assert link1['href'].value == self.tb_url

        feed_id = dom.getElementsByTagName('id')[0]
        assert feed_id.firstChild.data == tb_atom_url

    def test_one_entry(self):
        comment_id = addComment(self.tb['sec']['000'],
                                contributor='contributor',
                                message="hello world")

        doc = self.tb.comments_atom()
        dom = minidom.parseString(doc)

        assert len(dom.getElementsByTagName('entry')) == 1
        entry = dom.getElementsByTagName('entry')[0]

        assert (entry.getElementsByTagName('title')[0].firstChild.data ==
                "Comment by Contributor Test (contributor)")

        assert len(entry.getElementsByTagName('author')) == 1
        author = entry.getElementsByTagName('author')[0]
        assert (author.getElementsByTagName('name')[0].firstChild.data ==
                "Contributor Test (contributor)")

        assert (entry.getElementsByTagName('id')[0].firstChild.data ==
                self.tb_url + '/sec/000/' + comment_id)

        assert (entry.getElementsByTagName('summary')[0].firstChild.data ==
                "hello world")

    def test_html_summary(self):
        # some simple html
        addComment(self.tb['sec']['000'], contributor='contributor',
                   message="teh <em>html</em> comment & stuff")
        # a broken piece of html
        addComment(self.tb['sec']['000'], contributor='contributor',
                   message="so <p><b>hello<i>world</b>!</i>")

        doc = self.tb.comments_atom()
        dom = minidom.parseString(doc)
        entry1 = dom.getElementsByTagName('entry')[1]
        summary1 = entry1.getElementsByTagName('summary')[0]
        assert (summary1.toxml() ==
                '<summary type="html">teh &lt;em&gt;html&lt;/em&gt; '
                'comment &amp; stuff</summary>')

        entry2 = dom.getElementsByTagName('entry')[0]
        summary2 = entry2.getElementsByTagName('summary')[0]
        print summary2.toxml()
        assert (summary2.toxml() ==
                '<summary type="html">so &lt;p&gt;&lt;b&gt;hello&lt;i&gt;'
                'world&lt;/b&gt;!&lt;/i&gt;</summary>')

    def test_http_content_type(self):
        comment_id = addComment(self.tb['sec']['000'],
                                contributor='contributor',
                                message="hello world")
        transaction.commit()

        url = '/portal/myfolder/test-consultation/comments_atom'
        response = Request.blank(url).get_response(self.wsgi_request)
        assert response.status == '200 OK', repr(response)
        assert (response.headers['Content-Type'] ==
                'application/atom+xml; charset=utf-8')

        assert "hello world" in response.body

    def test_limit_by_date(self):
        def add_comment(msg, delta=timedelta()):
            para = self.tb['sec']['000']
            cid = addComment(para, contributor='contributor', message=msg)
            comment = para[cid]
            comment.comment_date = dt2DT(DT2dt(comment.comment_date) + delta)
            return comment

        add_comment("comment from today")
        add_comment("comment from yesterday", timedelta(days=-1))
        add_comment("comment from 2 days ago", timedelta(days=-2))
        add_comment("comment from last week", timedelta(days=-7))
        add_comment("comment from last month", timedelta(days=-30))

        doc = self.tb.comments_atom(days=3)
        dom = minidom.parseString(doc)
        comments = []
        for entry in dom.getElementsByTagName('entry'):
            comments.append(entry.getElementsByTagName('summary')[0].toxml())

        assert comments == [
            '<summary type="html">comment from today</summary>',
            '<summary type="html">comment from yesterday</summary>',
            '<summary type="html">comment from 2 days ago</summary>']
