from django import template

register = template.Library()

@register.filter(name='get_item')
def get_item(value, arg):
    print(value)
    print(arg)
    return value.get(arg, "")