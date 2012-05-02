import logging
import flask
import flatland as fl


log = logging.getLogger(__name__)


CommonFile = fl.Integer.using(optional=True) \
                       .with_properties(widget="file",
                                        widget_image=False)


def handle_request(session, root_element, old_flat={}):
    # TODO allow removing of files

    for element in root_element.all_children:
        if not isinstance(element, CommonFile):
            continue

        flat_name = element.flattened_name()
        log.debug('processing field %r', flat_name)

        uploaded_file = flask.request.files.get('%s-data' % flat_name)
        if uploaded_file:
            db_file = session.get_db_file()
            db_file.save_from(uploaded_file)
            log.debug('saving blob %r', db_file.id)
            element.set(db_file.id)

        else:
            old_value = old_flat.get(flat_name)
            element.set(old_value)

        log.debug('element.u = %r', element.u)
