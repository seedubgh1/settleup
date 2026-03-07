from django import template

register = template.Library()

@register.filter
def display_name(user):
    """Return full name if available, otherwise email."""
    return user.get_full_name() or user.email

@register.filter
def display_initials(user):
    """Return initials from name, or first letter of email if no name."""
    if user.get_full_name():
        parts = user.get_full_name().split()
        return ''.join(p[0].upper() for p in parts[:2])
    return user.email[0].upper()