from django import template

register = template.Library()

@register.filter
def split_complectation(value):
    if isinstance(value, str):
        return [item.strip() for item in value.split(",") if item.strip()]
    return []
