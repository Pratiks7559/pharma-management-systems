@login_required
def delete_invoice_series(request, series_id):
    """Delete invoice series"""
    if request.method == 'POST':
        try:
            series = InvoiceSeries.objects.get(series_id=series_id)
            series_name = series.series_name
            series.delete()
            return JsonResponse({'success': True, 'message': f'Series "{series_name}" deleted successfully'})
        except InvoiceSeries.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Series not found'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Invalid request method'})
