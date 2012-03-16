import scrubber
import simplejson
import time
from datetime import datetime

from naaya.content.document.document_item import addNyDocument
from Products.NaayaCore.managers.utils import slugify
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from ZPublisher import NotFound

preview_html_zpt = PageTemplateFile("zpt/preview.zpt", globals())

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


def forum_publish_save(context, REQUEST):
    scrub = scrubber.Scrubber().scrub
    response = {"status": "success"}
    content = REQUEST.form["content"]

    try:
        topic = context[REQUEST.form["topic"]]
    except KeyError:
        raise NotFound("Topic not found")

    if hasattr(topic, "forum_publish_objects"):
        content  = scrub(content)
        site = context.getSite()
        doc = get_document_or_create(site, title=TITLE)

         # update Naaya document
        doc.set_localpropvalue("body", site.gl_get_selected_language(), content)
        # doc.body = content
        doc.recatalogNyObject(doc)

        response["url"] = doc.absolute_url()
        REQUEST.RESPONSE.setHeader("Content-Type", "application/json")
        return simplejson.dumps(response)
    else:
        raise NotFound("No objects to publish")


def forum_publish_translations(context, request):
    trans = {}
    portal_i18n = context.getSite().getPortalI18n()
    for msg in LIST_OF_MESSAGES:
        trans[msg] = portal_i18n.get_translation(msg)

    request.RESPONSE.setHeader("Content-Type", "application/json")
    return simplejson.dumps(trans)


def forum_publish_save_object(context, REQUEST):
    response = {"status": "success"}

    request_content, request_context = REQUEST["content"], REQUEST["context"]
    if not isinstance(request_content, list):
        request_content = [request_content]
    if not isinstance(request_context, list):
        request_context = [request_context]

    # import pdb; pdb.set_trace()
    forum_publish_objects = []
    for item in zip(request_content, request_context):
        data = simplejson.loads(item[1])
        data["content"] = item[0]
        # from '17 Feb 2012 17:15:50' string to timestamp
        data["timestamp"] = int(time.mktime(time.strptime(data["date"], "%d %b %Y %H:%M:%S")))
        # data["timestamp"] = int(time.mktime(data["timestamp"].timetuple()))
        forum_publish_objects.append(data)

    try:
        topic = context[forum_publish_objects[0]["topic"]]
    except KeyError:
        raise NotFound("Topic not found")

    if not hasattr(topic.aq_base, "forum_publish_objects"):
        topic.forum_publish_objects = []
        topic.forum_publish_objects.append({
            "id": topic["id"],
            "title": topic["title"],
            "author": topic["author"],
            "date": topic["postdate"],
            "content": topic["description"],
            "timestamp": 0,
        })

    topic.forum_publish_objects.extend(forum_publish_objects)
    topic.forum_publish_objects = sorted(topic.forum_publish_objects,
                                         key=lambda k: k["timestamp"])

    response["url"] = "%s/forum_publish_preview/?topic=%s" % \
                      (context.absolute_url(), topic["title"])
    return simplejson.dumps(response)

def forum_publish_remove_object(context, REQUEST):
    response = {"status": "success"}
    id = REQUEST.form["id"]

    try:
        topic = context[REQUEST.form["topic"]]
    except KeyError:
        raise NotFound("Topic not found")


    if hasattr(topic.aq_base, "forum_publish_objects"):
        topic.forum_publish_objects = [
            i for i in topic.aq_base.forum_publish_objects if i["id"] != id
        ]
    else:
        raise NotFound
    return simplejson.dumps(response)


def forum_publish_preview(context, REQUEST):
    try:
        topic = context[REQUEST.form["topic"]]
    except KeyError:
        raise NotFound("Topic not found")

    forum_publish_objects = []
    if hasattr(topic.aq_base, "forum_publish_objects"):
        forum_publish_objects = topic.aq_base.forum_publish_objects

    return preview_html_zpt.__of__(context)(REQUEST, **{
        "forum_publish_objects": forum_publish_objects,
        "topic": REQUEST.form["topic"],
    })


def forum_publish_clear_objects(context, REQUEST):
    try:
        topic = context[REQUEST.form["topic"]]
    except KeyError:
        raise NotFound("Topic not found")

    if hasattr(topic.aq_base, "forum_publish_objects"):
        del topic.forum_publish_objects

    return simplejson.dumps({"status": "success"})


