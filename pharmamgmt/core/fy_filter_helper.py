"""
Year Filter Helper - Apply to all major views
Import this in views and use apply_fy_filter()
"""
from core.year_filter_utils import apply_year_filter

def apply_fy_filter(queryset, request, date_field='created_at'):
    """
    Wrapper function to apply financial year filter
    Usage: queryset = apply_fy_filter(queryset, request, 'invoice_date')
    """
    return apply_year_filter(queryset, request, date_field)
