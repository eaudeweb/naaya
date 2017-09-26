import scrubber
import simplejson
import time
from datetime import datetime

from naaya.content.document.document_item import addNyDocument

from Products.Naaya.NyFolder import addNyFolder
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

FOLDER = {
    "id": "folder-extracts",
    "title": "Folder of extracts",
}


def forum_publish_save_object(context, REQUEST):
    response = {"status": "success"}

    request_content, request_context = REQUEST["content"], REQUEST["context"]
    if not isinstance(request_content, list):
        request_content = [request_content]
    if not isinstance(request_context, list):
        request_context = [request_context]

    # process information from REQUES
    objects = _forum_publish_objects(request_content, request_context)
    topic = _get_topic(context, objects[0]["topic"])

    # add forum_publish_objects to topic
    if not hasattr(topic.aq_base, "forum_publish_objects"):
        topic.forum_publish_objects = {
            0: {
                "id": topic["id"],
                "title": topic["title"],
                "author": topic["author"],
                "date": topic["postdate"],
                "content": topic["description"],
            }
        }

    # process forum_publish_objects
    publish_objects = topic.forum_publish_objects
    for i, obj in enumerate(objects):
        # append to post instead of creating a new post
        if obj["timestamp"] in publish_objects.keys():
            publish_objects[obj["timestamp"]]["content"] += "<br /> %s" % obj["content"]
        else:
            publish_objects[obj["timestamp"]] = obj

    response["url"] = "%s/forum_publish_preview/?topic=%s" % \
                      (context.absolute_url(), topic["id"])
    return simplejson.dumps(response)


def forum_publish_preview(context, REQUEST):
    topic = _get_topic(context, REQUEST.form["topic"])
    folder = get_or_create_folder(site=context.getSite(),
                                  id=FOLDER["id"],
                                  title=FOLDER["title"])

    documents = folder.objectValues()
    forum_publish_objects = []
    if hasattr(topic.aq_base, "forum_publish_objects"):
        forum_publish_objects = topic.aq_base.forum_publish_objects

    return preview_html_zpt.__of__(context)(REQUEST, **{
        "forum_publish_objects": forum_publish_objects,
        "topic": REQUEST.form["topic"],
        "documents": documents,
    })


def forum_publish_save(context, REQUEST):
    scrub = scrubber.Scrubber().scrub
    response = {"status": "success"}
    content = REQUEST.form["content"]
    topic = _get_topic(context, REQUEST.form["topic"])
    filename = REQUEST.form["filename"]

    if hasattr(topic, "forum_publish_objects"):
        content  = scrub(content)
        site = context.getSite()
        doc = get_document_or_create(site, title=filename)

        doc_content = doc.getLocalAttribute("body",
                                            site.gl_get_selected_language())
        doc_content += content
         # update Naaya document
        doc.set_localpropvalue("body", site.gl_get_selected_language(),
                               doc_content)
        # doc.body = content
        doc.recatalogNyObject(doc)

        # clear preview document
        _clear_preview(context, REQUEST.form["topic"])

        response["url"] = doc.absolute_url()
        REQUEST.RESPONSE.setHeader("Content-Type", "application/json")
        return simplejson.dumps(response)
    else:
        raise NotFound("No objects to publish")


def forum_publish_remove_object(context, REQUEST):
    response = {"status": "success"}
    timestamp = int(REQUEST.form["timestamp"])
    topic = _get_topic(context, REQUEST.form["topic"])

    if (hasattr(topic.aq_base, "forum_publish_objects") and
        timestamp in topic.forum_publish_objects.keys()):
        del topic.forum_publish_objects[timestamp]
    else:
        raise NotFound
    return simplejson.dumps(response)


def get_document_or_create(site, title):
    folder = site[FOLDER["id"]]

    try:
        doc = folder[slugify(title, removelist=[])]
    except KeyError:
        doc_id = addNyDocument(folder, title=title, submitted=1)
        doc = folder[doc_id]
    return doc


def get_or_create_folder(site, id, title):
    """
    Creates a folder if it does't exist
    """
    try:
        folder = site[id]
    except KeyError:
        folder = site[addNyFolder(site, id=id, title=title)]
    return folder


def forum_publish_clear_preview(context, REQUEST):
    _clear_preview(context, REQUEST.form["topic"])
    return simplejson.dumps({"status": "success"})


def forum_publish_translations(context, request):
    trans = {}
    portal_i18n = context.getSite().getPortalI18n()
    for msg in LIST_OF_MESSAGES:
        trans[msg] = portal_i18n.get_translation(msg)

    request.RESPONSE.setHeader("Content-Type", "application/json")
    return simplejson.dumps(trans)


def _forum_publish_objects(content, context):
    objects = []
    for item in zip(content, context):
        data = simplejson.loads(item[1])
        data["content"] = item[0]
        # from '17 Feb 2012 17:15:50' string to timestamp
        data["timestamp"] = time.strptime(data["date"], "%d %b %Y %H:%M:%S")
        data["timestamp"] = int(time.mktime(data["timestamp"]))
        objects.append(data)
    return objects


def _get_topic(context, title):
    try:
        return context[title]
    except KeyError:
        raise NotFound("Topic not found")


def _clear_preview(context, topic):
    topic = _get_topic(context, topic)
    if hasattr(topic.aq_base, "forum_publish_objects"):
        del topic.forum_publish_objects
        return True
    return False


