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


# groups/templatetags/group_filters.py

@register.filter
def count_completed(enrollments):
    """Count enrollments that should check payment"""
    return sum(1 for item in enrollments if item['should_check_payment'])

@register.filter
def count_completed_not_paid(enrollments):
    """Count completed enrollments that are not fully paid"""
    return sum(1 for item in enrollments 
               if item['should_check_payment'] and not item['payment_status']['is_fully_paid'])



@register.filter
def count_fully_paid(enrollments):
    """Count enrollments with fully paid status"""
    return sum(1 for item in enrollments if item['payment_status']['is_fully_paid'])