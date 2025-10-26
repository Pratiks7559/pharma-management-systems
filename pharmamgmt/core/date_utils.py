"""
Unified Date Utilities for DDMMYYYY format handling
Provides consistent date parsing and formatting across the application
"""
from datetime import datetime, date
from django.core.exceptions import ValidationError
from django.utils import timezone


def parse_ddmmyyyy_date(date_str):
    """
    Parse DDMMYYYY string or legacy formats to date object
    
    Args:
        date_str (str): Date string in DDMMYYYY or legacy format
        
    Returns:
        date: Parsed date object
        
    Raises:
        ValidationError: If date format is invalid
    """
    if not date_str:
        return None
        
    date_str = str(date_str).strip()
    
    # Handle YYYY-MM-DD format (already correct)
    if len(date_str) == 10 and '-' in date_str:
        try:
            return datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            pass
    
    # Handle MM-YYYY format (common for expiry dates)
    if len(date_str) == 7 and date_str.count('-') == 1:
        try:
            month, year = date_str.split('-')
            month = int(month)
            year = int(year)
            
            # Validate month and year
            if 1 <= month <= 12 and 1900 <= year <= 2100:
                # Return last day of the month for expiry dates
                last_day = 31 if month in [1,3,5,7,8,10,12] else 30
                if month == 2:
                    last_day = 29 if year % 4 == 0 else 28
                return date(year, month, last_day)
        except (ValueError, TypeError):
            pass
    
    # Try to convert legacy formats first
    if len(date_str) != 8 or not date_str.isdigit():
        converted = convert_legacy_dates(date_str)
        if converted != date_str:
            date_str = converted
    
    # Handle DDMMYYYY format
    if len(date_str) == 8 and date_str.isdigit():
        day = int(date_str[:2])
        month = int(date_str[2:4])
        year = int(date_str[4:8])
        
        try:
            return date(year, month, day)
        except ValueError as e:
            raise ValidationError(f"Invalid date combination: {day:02d}/{month:02d}/{year}")
    
    # Get specific validation error only if no format matched
    error_message = get_date_validation_error(date_str)
    if error_message:
        raise ValidationError(error_message)
    
    # If no format matched, return None to avoid raising error for MM-YYYY format
    return None


def format_date_for_display(date_obj):
    """
    Format date object to DDMMYYYY string for display
    
    Args:
        date_obj (date): Date object to format
        
    Returns:
        str: Date string in DDMMYYYY format
    """
    if not date_obj:
        return ""
        
    if isinstance(date_obj, str):
        # Try to parse if it's a string
        try:
            if len(date_obj) == 10 and '-' in date_obj:
                date_obj = datetime.strptime(date_obj, '%Y-%m-%d').date()
            elif len(date_obj) == 8 and date_obj.isdigit():
                # Already in DDMMYYYY format
                return date_obj
            elif len(date_obj) == 7 and date_obj.count('-') == 1:
                # MM-YYYY format - keep as is for expiry dates
                return date_obj
            else:
                # Try to convert legacy format
                converted = convert_legacy_dates(date_obj)
                if len(converted) == 8 and converted.isdigit():
                    return converted
                return date_obj
        except ValueError:
            return date_obj
    
    return date_obj.strftime('%d%m%Y')


def format_date_for_backend(date_obj):
    """
    Format date object to YYYY-MM-DD string for backend storage
    
    Args:
        date_obj (date): Date object to format
        
    Returns:
        str: Date string in YYYY-MM-DD format
    """
    if not date_obj:
        return ""
        
    if isinstance(date_obj, str):
        # If already in backend format, return as-is
        if len(date_obj) == 10 and '-' in date_obj:
            return date_obj
        # Handle MM-YYYY format for expiry dates
        elif len(date_obj) == 7 and date_obj.count('-') == 1:
            try:
                month, year = date_obj.split('-')
                month = int(month)
                year = int(year)
                # Return last day of month for expiry dates
                last_day = 31 if month in [1,3,5,7,8,10,12] else 30
                if month == 2:
                    last_day = 29 if year % 4 == 0 else 28
                return f"{year}-{month:02d}-{last_day:02d}"
            except (ValueError, TypeError):
                return date_obj
        # Try to parse DDMMYYYY or legacy format
        try:
            parsed_date = parse_ddmmyyyy_date(date_obj)
            if parsed_date:
                return parsed_date.strftime('%Y-%m-%d')
            return date_obj
        except ValidationError:
            return date_obj
    
    return date_obj.strftime('%Y-%m-%d')


def convert_legacy_dates(date_str):
    """
    Convert legacy date formats to DDMMYYYY
    Handles MM, DDMM, DD/MM, MM-YYYY formats
    
    Args:
        date_str (str): Date string in various legacy formats
        
    Returns:
        str: Date string in DDMMYYYY format or original if conversion fails
    """
    if not date_str:
        return ""
    
    date_str = str(date_str).strip()
    current_year = datetime.now().year
    
    # Handle MM format (2 digits) - for expiry dates, use last day of month
    if len(date_str) == 2 and date_str.isdigit():
        month = int(date_str)
        if 1 <= month <= 12:
            # Use last day of month for expiry dates
            last_day = 31 if month in [1,3,5,7,8,10,12] else 30
            if month == 2:
                last_day = 29 if current_year % 4 == 0 else 28
            return f"{last_day:02d}{month:02d}{current_year}"
    
    # Handle DDMM format (4 digits) - check if it's day-month or month-year
    if len(date_str) == 4 and date_str.isdigit():
        first_two = int(date_str[:2])
        last_two = int(date_str[2:4])
        
        # If first two digits are valid day (1-31) and last two are valid month (1-12)
        if 1 <= first_two <= 31 and 1 <= last_two <= 12:
            # DDMM format - auto-complete year
            return date_str + str(current_year)
        # If first two digits are valid month (1-12) - MMYY format
        elif 1 <= first_two <= 12:
            month = first_two
            year = 2000 + last_two
            # Use last day of month for expiry dates
            last_day = 31 if month in [1,3,5,7,8,10,12] else 30
            if month == 2:
                last_day = 29 if year % 4 == 0 else 28
            return f"{last_day:02d}{month:02d}{year}"
    
    # Handle DD/MM format
    if '/' in date_str and len(date_str.split('/')) == 2:
        try:
            day, month = date_str.split('/')
            return f"{day.zfill(2)}{month.zfill(2)}{current_year}"
        except ValueError:
            pass
    
    # Handle MM-YYYY format (for expiry dates)
    if '-' in date_str and len(date_str.split('-')) == 2:
        try:
            parts = date_str.split('-')
            month = int(parts[0])
            year = int(parts[1])
            
            # Handle 2-digit years
            if year < 100:
                year = 2000 + year
            
            # Validate month and year
            if 1 <= month <= 12 and 1900 <= year <= 2100:
                # Use last day of month for expiry dates
                last_day = 31 if month in [1,3,5,7,8,10,12] else 30
                if month == 2:
                    last_day = 29 if year % 4 == 0 else 28
                return f"{last_day:02d}{month:02d}{year}"
        except (ValueError, TypeError):
            pass
    
    return date_str


def validate_ddmmyyyy_format(date_str):
    """
    Validate DDMMYYYY format or legacy formats that can be converted
    
    Args:
        date_str (str): Date string to validate
        
    Returns:
        bool: True if valid or convertible, False otherwise
    """
    if not date_str:
        return False
    
    date_str = str(date_str).strip()
    
    # Check for MM-YYYY format (common for expiry dates)
    if len(date_str) == 7 and date_str.count('-') == 1:
        try:
            month, year = date_str.split('-')
            month = int(month)
            year = int(year)
            
            if month < 1 or month > 12:
                return False
            if year < 1900 or year > 2100:
                return False
            
            return True
        except (ValueError, TypeError):
            return False
    
    # Check if already in DDMMYYYY format
    if len(date_str) == 8 and date_str.isdigit():
        try:
            day = int(date_str[:2])
            month = int(date_str[2:4])
            year = int(date_str[4:8])
            
            if month < 1 or month > 12:
                return False
            if day < 1 or day > 31:
                return False
            if year < 1900 or year > 2100:
                return False
            
            # Check for valid day in month
            date(year, month, day)
            return True
        except ValueError:
            return False
    
    # Check if it's a convertible legacy format
    try:
        converted = convert_legacy_dates(date_str)
        if converted != date_str and len(converted) == 8 and converted.isdigit():
            return validate_ddmmyyyy_format(converted)
    except:
        pass
    
    return False


def get_date_validation_error(date_str):
    """
    Get specific validation error message for date string
    
    Args:
        date_str (str): Date string to validate
        
    Returns:
        str: Specific error message or None if valid
    """
    if not date_str:
        return "Date is required"
    
    date_str = str(date_str).strip()
    
    # Check for MM-YYYY format first (common for expiry dates)
    if len(date_str) == 7 and date_str.count('-') == 1:
        try:
            month, year = date_str.split('-')
            month = int(month)
            year = int(year)
            
            if month < 1 or month > 12:
                return f"Invalid month '{month:02d}'. Please enter a month between 01-12"
            
            if year < 1900 or year > 2100:
                return f"Invalid year '{year}'. Please enter a year between 1900-2100"
            
            return None  # Valid MM-YYYY format
        except (ValueError, TypeError):
            return "Invalid MM-YYYY format. Please enter like 12-2026"
    
    # Check DDMMYYYY format
    if len(date_str) != 8 or not date_str.isdigit():
        # Try legacy format conversion
        converted = convert_legacy_dates(date_str)
        if converted != date_str and len(converted) == 8 and converted.isdigit():
            date_str = converted
        else:
            return "Please enter date in DDMMYYYY format (e.g., 15012024) or MM-YYYY format (e.g., 12-2026)"
    
    try:
        day = int(date_str[:2])
        month = int(date_str[2:4])
        year = int(date_str[4:8])
        
        if month < 1 or month > 12:
            return f"Invalid month '{month:02d}'. Please enter a month between 01-12"
        
        if day < 1 or day > 31:
            return f"Invalid day '{day:02d}'. Please enter a day between 01-31"
        
        if year < 1900 or year > 2100:
            return f"Invalid year '{year}'. Please enter a year between 1900-2100"
        
        # Check for valid day in month
        test_date = date(year, month, day)
        if test_date.day != day or test_date.month != month or test_date.year != year:
            return f"Invalid date combination: {day:02d}/{month:02d}/{year}"
        
        return None  # Valid date
        
    except ValueError as e:
        return f"Invalid date: {str(e)}"


def get_date_display_format(date_obj):
    """
    Get human-readable date format (DD/MM/YYYY)
    
    Args:
        date_obj (date): Date object to format
        
    Returns:
        str: Date string in DD/MM/YYYY format
    """
    if not date_obj:
        return ""
        
    if isinstance(date_obj, str):
        try:
            if len(date_obj) == 8 and date_obj.isdigit():
                # DDMMYYYY format
                return f"{date_obj[:2]}/{date_obj[2:4]}/{date_obj[4:8]}"
            elif len(date_obj) == 10 and '-' in date_obj:
                # YYYY-MM-DD format
                date_obj = datetime.strptime(date_obj, '%Y-%m-%d').date()
            elif len(date_obj) == 7 and date_obj.count('-') == 1:
                # MM-YYYY format - convert to display format
                month, year = date_obj.split('-')
                return f"{month}/{year}"
            else:
                # Try to convert legacy format
                converted = convert_legacy_dates(date_obj)
                if len(converted) == 8 and converted.isdigit():
                    return f"{converted[:2]}/{converted[2:4]}/{converted[4:8]}"
                return date_obj
        except ValueError:
            return date_obj
    
    return date_obj.strftime('%d/%m/%Y')


def get_current_datetime():
    """
    Get current timezone-aware datetime
    
    Returns:
        datetime: Current timezone-aware datetime
    """
    return timezone.now()


def get_current_date():
    """
    Get current date
    
    Returns:
        date: Current date
    """
    return timezone.now().date()