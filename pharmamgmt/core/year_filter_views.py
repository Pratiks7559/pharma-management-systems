from django.http import JsonResponse
from django.views.decorators.http import require_POST

@require_POST
def set_year_filter(request):
    year = request.POST.get('year')
    if year:
        try:
            year = int(year)
            request.session['selected_year'] = year
            return JsonResponse({'success': True, 'year': year})
        except ValueError:
            return JsonResponse({'success': False, 'error': 'Invalid year'})
    return JsonResponse({'success': False, 'error': 'Year not provided'})
