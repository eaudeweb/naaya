available_migrations = {}

def register_migration(metatype_from, metatype_to):
    def decorator(func):
        if metatype_from not in available_migrations:
            available_migrations[metatype_from] = {}
        available_migrations[metatype_from][metatype_to] = func
        return func
    return decorator

def perform_migration(context, widget_id, new_meta_type):
    migrate = available_migrations[context[widget_id].meta_type][new_meta_type]
    migrate(context, widget_id)

def basic_replace(context, widget_id, addWidgetFunction):
    # save whatever information we need
    old_widget = context[widget_id]
    old_objects_order = [o['id'] for o in context._objects]

    # swap with new widget
    context.manage_delObjects([widget_id])
    new_id = addWidgetFunction(context, widget_id, old_widget.title)
    assert new_id == widget_id
    new_widget = context[widget_id]

    # restore order of child objects
    new_objects = dict( (o['id'], o) for o in context._objects )
    assert set(old_objects_order) == set(new_objects)
    context._objects = tuple(new_objects[i] for i in old_objects_order)

    # restore widget properties
    new_widget._local_properties['title'] = \
            old_widget._local_properties['title']
    new_widget._local_properties['tooltips'] = \
            old_widget._local_properties['tooltips']
    new_widget.required = old_widget.required
    new_widget.sortorder = old_widget.sortorder
    new_widget.__ac_local_roles__ = old_widget.__ac_local_roles__

    return new_widget

@register_migration('Naaya String Widget', 'Naaya Text Area Widget')
def migrate_string_to_textarea(context, widget_id):
    from Products.NaayaWidgets.widgets.TextAreaWidget import addTextAreaWidget

    new_widget = basic_replace(context, widget_id, addTextAreaWidget)

@register_migration('Naaya Radio Widget', 'Naaya Checkboxes Widget')
def migrate_radio_to_checkboxes(context, widget_id):
    from Products.NaayaWidgets.widgets.CheckboxesWidget import \
            addCheckboxesWidget

    old_widget = context[widget_id]
    assert old_widget.add_extra_choice is False

    new_widget = basic_replace(context, widget_id, addCheckboxesWidget)

    # properties specific to Radio/Checkboxes widgets
    new_widget._local_properties['choices'] = \
            old_widget._local_properties['choices']
    new_widget.display = old_widget.display

    # need to update answers because Checkboxes stores a list
    for answer in context.objectValues(['Naaya Survey Answer']):
        value = getattr(answer, widget_id, None)
        if value is not None:
            setattr(answer, widget_id, [value])

@register_migration('Naaya String Widget', 'Naaya Localized String Widget')
def migrate_string_to_localized_string(context, widget_id):
    from Products.NaayaWidgets.widgets.LocalizedStringWidget import \
            addLocalizedStringWidget

    old_widget = context[widget_id]
    assert old_widget.localized is False

    new_widget = basic_replace(context, widget_id, addLocalizedStringWidget)

    for answer in context.objectValues(['Naaya Survey Answer']):
        value = getattr(answer.aq_explicit, widget_id, None)
        if value is not None:
            lang = context.gl_get_default_language()
            answer.set_property(widget_id, {lang: value})

@register_migration('Naaya Localized String Widget',
                    'Naaya Localized Text Area Widget')
def migrate_localized_string_to_localized_textarea(context, widget_id):
    from Products.NaayaWidgets.widgets.LocalizedTextAreaWidget import \
            addLocalizedTextAreaWidget

    new_widget = basic_replace(context, widget_id, addLocalizedTextAreaWidget)


@register_migration('Naaya Text Area Widget',
                    'Naaya Localized Text Area Widget')
def migrate_textarea_to_localized_textarea(context, widget_id):
    from Products.NaayaWidgets.widgets.LocalizedTextAreaWidget import \
            addLocalizedTextAreaWidget

    old_widget = context[widget_id]
    rows = old_widget.rows
    columns = old_widget.columns
    assert old_widget.localized is False

    new_widget = basic_replace(context, widget_id, addLocalizedTextAreaWidget)
    new_widget.rows = rows
    new_widget.columns = columns

    for answer in context.objectValues(['Naaya Survey Answer']):
        value = getattr(answer.aq_explicit, widget_id, None)
        if value is not None:
            lang = context.gl_get_default_language()
            answer.set_property(widget_id, {lang: value})

@register_migration('Naaya Localized String Widget', 'Naaya String Widget')
def migrate_localized_string_to_string(context, widget_id):
    from Products.NaayaWidgets.widgets.StringWidget import \
            addStringWidget

    old_widget = context[widget_id]
    assert old_widget.localized is True

    new_widget = basic_replace(context, widget_id, addStringWidget)

    for answer in context.objectValues(['Naaya Survey Answer']):
        value = answer.getLocalProperty(widget_id, lang=context.gl_get_default_language())
        if value is not None:
            answer.set_property(widget_id, value)
            if answer._local_properties.has_key(widget_id):
                del answer._local_properties[widget_id]

@register_migration('Naaya Localized Text Area Widget',
                    'Naaya Text Area Widget')
def migrate_localized_textarea_to_textarea(context, widget_id):
    from Products.NaayaWidgets.widgets.TextAreaWidget import \
            addTextAreaWidget

    old_widget = context[widget_id]
    rows = old_widget.rows
    columns = old_widget.columns
    assert old_widget.localized is True

    new_widget = basic_replace(context, widget_id, addTextAreaWidget)
    new_widget.rows = rows
    new_widget.columns = columns

    for answer in context.objectValues(['Naaya Survey Answer']):
        value = answer.getLocalProperty(widget_id, lang=context.gl_get_default_language())
        if value is not None:
            answer.set_property(widget_id, value)
            if answer._local_properties.has_key(widget_id):
                del answer._local_properties[widget_id]

@register_migration('Naaya Localized Text Area Widget',
                    'Naaya Localized String Widget')
def migrate_localized_textarea_to_localized_string(context, widget_id):
    from Products.NaayaWidgets.widgets.LocalizedStringWidget import \
            addLocalizedStringWidget

    new_widget = basic_replace(context, widget_id, addLocalizedStringWidget)
