from core.year_filter_utils import get_current_financial_year

class YearFilterMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Set default financial year if not set
        if 'selected_year' not in request.session:
            request.session['selected_year'] = get_current_financial_year()
        
        response = self.get_response(request)
        return response
