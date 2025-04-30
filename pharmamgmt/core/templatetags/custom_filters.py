from django import template
from django.template.defaultfilters import floatformat

register = template.Library()

@register.filter
def currency(value):
    """Format a value as currency"""
    try:
        value = float(value)
        return f"₹{floatformat(value, 2)}"
    except (ValueError, TypeError):
        return ""

@register.filter
def percentage(value):
    """Format a value as percentage"""
    try:
        value = float(value)
        return f"{floatformat(value, 2)}%"
    except (ValueError, TypeError):
        return ""

@register.filter
def multiply(value, arg):
    """Multiply the value by the argument"""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return ""

@register.filter
def subtract(value, arg):
    """Subtract the argument from the value"""
    try:
        return float(value) - float(arg)
    except (ValueError, TypeError):
        return ""

@register.filter
def add(value, arg):
    """Add the argument to the value"""
    try:
        return float(value) + float(arg)
    except (ValueError, TypeError):
        return ""

@register.filter
def divide(value, arg):
    """Divide the value by the argument"""
    try:
        arg = float(arg)
        if arg == 0:
            return 0
        return float(value) / arg
    except (ValueError, TypeError):
        return ""

@register.filter
def get_dict_value(dictionary, key):
    """Get a value from a dictionary by key"""
    if not dictionary:
        return ""
    return dictionary.get(key, "")

@register.simple_tag
def calculate_balance(invoice_total, invoice_paid):
    """Calculate balance amount for an invoice"""
    try:
        return float(invoice_total) - float(invoice_paid)
    except (ValueError, TypeError):
        return 0
