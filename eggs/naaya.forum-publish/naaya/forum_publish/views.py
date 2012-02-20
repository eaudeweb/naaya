import scrubber
import simplejson

from naaya.content.document.document_item import addNyDocument
from Products.NaayaCore.managers.utils import slugify

LIST_OF_MESSAGES = [
    "Publish",
    "Please select a range",
    "Please select a range in the same container",
    "No published text",
    "Publish",
    "Cancel",
    "Remove",
    "Alert",
]

TITLE = "Draft"

def get_document_or_create(site, title):
    folder = site["forum_publish"]
    try:
        doc = folder[slugify(title)]
    except KeyError:
        doc_id = addNyDocument(folder, title=title, submitted=1)
        doc = folder[doc_id]
    return doc

def forum_publish_save(context, request):
    scrub = scrubber.Scrubber().scrub
    response = {"status": "success"}

    content = request.form["content"]
    author = request.form["author"]
    date = request.form["date"]

    site = context.getSite()
    doc = get_document_or_create(site, title=TITLE)

    if not isinstance(content, list):
        content = [content]
    if not isinstance(author, list):
        author = [author]
    if not isinstance(date, list):
        date = [date]

    # sanitize content and wrap div around it
    content = ["<div class='doc-content'>%s</div>" % c for c in content]
    author = [
        "<div class='doc-date'>%s, <div class='doc-author'>%s</div></div>"
            % (d, a) for a in author for d in date
    ]
    # dom => [("<div class='content'>%s</div>", "<div class='author'>%s</div>")]
    dom = zip(content, author)

    body = ""
    for element in dom:
        body += "".join(element)
    body = scrub(body)

    # update Naaya document
    doc.body = doc.body + body
    doc.recatalogNyObject(doc)

    response["url"] = doc.absolute_url()
    request.RESPONSE.setHeader("Content-Type", "application/json")
    return simplejson.dumps(response)


def forum_publish_translations(context, request):
    trans = {}
    portal_i18n = context.getSite().getPortalI18n()
    for msg in LIST_OF_MESSAGES:
        trans[msg] = portal_i18n.get_translation(msg)

    request.RESPONSE.setHeader("Content-Type", "application/json")
    return simplejson.dumps(trans)
