from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """Безопасно возвращает значение по ключу из словаря"""
    if isinstance(dictionary, dict):
        return dictionary.get(key)
    return None

@register.filter
def subtract(value, arg):
    """Вычитает arg из value"""
    return value - arg

@register.simple_tag
def increment(value):
    """Увеличивает число на 1"""
    return value + 1