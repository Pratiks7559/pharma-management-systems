from django import template
from decimal import Decimal
import locale

register = template.Library()

# Try to set locale for Indian Rupee formatting
try:
    locale.setlocale(locale.LC_ALL, 'en_IN.UTF-8')
except:
    # Fallback to default locale if Indian locale not available
    locale.setlocale(locale.LC_ALL, '')

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

@register.filter
def inr_format(value):
    """
    Format a number as Indian Rupees (INR).
    
    Examples:
        1234.56 -> ₹ 1,234.56
        1234567.89 -> ₹ 12,34,567.89
    """
    try:
        # Convert to float first
        value = float(value)
        
        # Format with commas using Indian numbering system
        if value < 0:
            sign = "-"
            value = abs(value)
        else:
            sign = ""
            
        # First format with conventional commas
        formatted = f"{value:,.2f}"
        
        # Handle special case for Indian format
        parts = formatted.split('.')
        integer_part = parts[0]
        
        # Don't format small numbers
        if len(integer_part.replace(',', '')) <= 3:
            return f"₹ {sign}{formatted}"
        
        # Custom format for Indian system (lakh, crore)
        # First remove existing commas
        integer_part = integer_part.replace(',', '')
        
        # Format in Indian style (3,2,2,...)
        result = integer_part[-3:]  # Last 3 digits
        integer_part = integer_part[:-3]  # Remaining digits
        
        # Add commas every 2 digits
        while integer_part:
            result = integer_part[-2:] + ',' + result if integer_part[-2:] else integer_part + ',' + result
            integer_part = integer_part[:-2]
        
        # Re-combine with decimal part
        if len(parts) > 1:
            return f"₹ {sign}{result}.{parts[1]}"
        else:
            return f"₹ {sign}{result}"
    except (ValueError, TypeError):
        return "₹ 0.00"