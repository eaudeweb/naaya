from django import template
from django.utils.safestring import mark_safe
from sugar import markup


register = template.Library()


@register.filter
def get_answers(section, category):
    return section.filter(category=category)


@register.assignment_tag
def get_widget_for_category(category, instance=None):
    return category.get_widget(instance)


@register.assignment_tag
def assign(value):
    return value


@register.filter
def pretty_hstore(value):
    page = markup.page()
    page.ul()
    for k, v in value.items():
        if v == '1':
            page.li()
            page.span(k.title())
            page.li.close()
    page.ul.close()
    return mark_safe(page)