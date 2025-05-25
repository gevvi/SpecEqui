from django import template
import homepage.views as views

register = template.Library()


@register.simple_tag()
def get_categories():
    return views.menu
