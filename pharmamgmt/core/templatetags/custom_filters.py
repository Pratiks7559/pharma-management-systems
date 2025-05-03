from django import template
from decimal import Decimal

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

@register.filter
def divide(value, arg):
    """Divides the value by the arg."""
    try:
        arg = float(arg)
        if arg == 0:
            return 0
        return float(value) / arg
    except (ValueError, TypeError, ZeroDivisionError):
        return 0

@register.filter
def multiply(value, arg):
    """Multiplies the value by the arg."""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0

@register.filter
def percentage(value, arg=100):
    """Calculates value as a percentage of arg."""
    try:
        return (float(value) / float(arg)) * 100
    except (ValueError, TypeError, ZeroDivisionError):
        return 0

@register.filter
def sum_field(value, field_name):
    """
    Returns the sum of a specified field for a list of dictionaries or objects.
    
    Usage:
    {{ queryset|sum_field:'field_name' }}
    """
    try:
        total = 0
        for item in value:
            # Handle both dictionary-like and object-like access
            try:
                # Dictionary-like access
                val = item[field_name]
            except (KeyError, TypeError):
                try:
                    # Object-like access
                    val = getattr(item, field_name)
                except (AttributeError, TypeError):
                    val = 0
                    
            # Try to convert to numeric value
            try:
                if isinstance(val, (int, float, Decimal)):
                    total += float(val)
                else:
                    total += float(val or 0)
            except (ValueError, TypeError):
                # Skip if we can't convert to a number
                pass
                
        return total
    except Exception:
        return 0