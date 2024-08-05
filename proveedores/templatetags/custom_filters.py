from django import template
from datetime import datetime

register = template.Library()

@register.filter
def formato_fecha(value):
    try:

        fecha = datetime.strptime(value, '%Y-%m-%d')
        return fecha.strftime('%d-%m-%Y')
    except (ValueError, TypeError):
        return ""


@register.filter
def formato_fecha_hora(value):
    try:
        value = value.replace('T', ' ')
        fecha = datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
        return fecha.strftime('%d-%m-%Y %H:%M:%S')
    except (ValueError, TypeError):
        return ""
@register.filter
def formatear_numero(value):
    try:
        value = float(value)
        return "{:,.2f}".format(value).replace(",", "X").replace(".", ",").replace("X", ".")
    except (ValueError, TypeError):
        return ""

@register.filter
def subtract(value, arg):
    return float(value) - float(arg)