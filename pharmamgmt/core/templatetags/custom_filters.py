from django import template

register = template.Library()

@register.filter
def sub(value, arg):
    """Subtracts the arg from the value."""
    try:
        return float(value) - float(arg)
    except (ValueError, TypeError):
        try:
            return value - arg
        except Exception:
            return 0

@register.filter
def currency(value):
    """Formats a value as a currency (₹)."""
    try:
        return f"₹ {float(value):,.2f}"
    except (ValueError, TypeError):
        return f"₹ 0.00"

@register.filter
def subtract(value, arg):
    """Alias for sub filter."""
    return sub(value, arg)

@register.filter
def add(value, arg):
    """Adds the arg to the value."""
    try:
        return float(value) + float(arg)
    except (ValueError, TypeError):
        try:
            return value + arg
        except Exception:
            return 0

@register.filter
def absolute(value):
    """Returns the absolute value."""
    try:
        return abs(float(value))
    except (ValueError, TypeError):
        return 0