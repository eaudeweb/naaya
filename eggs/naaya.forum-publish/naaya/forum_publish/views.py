import scrubber
import simplejson

from naaya.content.document.document_item import addNyDocument

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

def forum_publish_save(context, request):
    scrub = scrubber.Scrubber().scrub
    response = {"status": "success"}

    content = request.form["content"]
    author = request.form["author"]
    title = "Draft"

    site = context.getSite()
    folder = site["forum_publish"]

    if not isinstance(content, list):
        content = [content]
    if not isinstance(author, list):
        author = [author]

    # sanitize content and wrap div around it
    content = ["<div class='content'>%s</div>" % c for c in content]
    author = ["<div class='author'>%s</div>" % a for a in author]
    # dom => [("<div class='content'>%s</div>", "<div class='author'>%s</div>")]
    dom = zip(content, author)

    body = ""
    for element in dom:
        body += "".join(element)
    body = scrub(body)

    # create Naaya document
    doc_id = addNyDocument(folder, title=title, body=body, submitted=1)
    doc = folder[doc_id]
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
