from django import template
from datetime import date, timedelta

register = template.Library()


@register.filter(name='get_value')
def get_value(cat, user):
    return cat.value(user)


@register.filter(name='has_items')
def has_children(cat, user):
    return cat.has_items(user)


@register.filter(name='children_value')
def children_value(cat, user):
    return cat.has_items(user)


@register.filter(name='item_count')
def item_count(cat, user):
    return cat.item_count(user)


@register.filter(name='children_item_count')
def children_item_count(cat, user):
    return cat.children_item_count(user)


@register.filter(name='format_date')
def format_date(date, user):
	if user.prefs.date_format == 'MM/DD/YYYY':
		return date.strftime('%m/%d/%Y')
	elif user.prefs.date_format == 'DD/MM/YYYY':
		return date.strftime('%d/%m/%Y')
