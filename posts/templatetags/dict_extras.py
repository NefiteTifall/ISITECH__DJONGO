from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """Filtre pour accéder aux valeurs d'un dictionnaire dans les templates Django"""
    return dictionary.get(key)

@register.filter
def to_str(value):
    """Convertit une valeur en string"""
    return str(value)