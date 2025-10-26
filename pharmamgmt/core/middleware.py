import time
import logging
from django.db import connection
from django.http import JsonResponse

logger = logging.getLogger(__name__)

class DatabaseRetryMiddleware:
    """
    Middleware to handle database locking issues and retry operations
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        max_retries = 3
        retry_delay = 0.1  # 100ms
        
        for attempt in range(max_retries):
            try:
                response = self.get_response(request)
                return response
            except Exception as e:
                error_msg = str(e).lower()
                
                # Check if it's a database locking error
                if 'database is locked' in error_msg or 'database locked' in error_msg:
                    if attempt < max_retries - 1:
                        logger.warning(f"Database locked, retrying attempt {attempt + 1}/{max_retries}")
                        time.sleep(retry_delay * (attempt + 1))  # Exponential backoff
                        continue
                    else:
                        logger.error(f"Database locked after {max_retries} attempts")
                        if request.headers.get('Content-Type') == 'application/json' or request.path.startswith('/api/'):
                            return JsonResponse({
                                'success': False,
                                'error': 'Database is temporarily busy. Please try again in a moment.'
                            }, status=503)
                        else:
                            # For regular requests, let Django handle it normally
                            raise
                else:
                    # Not a database locking error, re-raise
                    raise
        
        # This should never be reached, but just in case
        return self.get_response(request)

    def process_exception(self, request, exception):
        """
        Handle exceptions that occur during request processing
        """
        error_msg = str(exception).lower()
        
        if 'database is locked' in error_msg or 'database locked' in error_msg:
            logger.error(f"Database locked exception: {exception}")
            
            if request.headers.get('Content-Type') == 'application/json' or request.path.startswith('/api/'):
                return JsonResponse({
                    'success': False,
                    'error': 'Database is temporarily busy. Please try again in a moment.'
                }, status=503)
        
        # Return None to let Django handle other exceptions normally
        return None


class DatabaseConnectionMiddleware:
    """
    Middleware to ensure proper database connection handling
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            response = self.get_response(request)
            return response
        finally:
            # Ensure database connections are properly closed
            if connection.connection:
                connection.close()

    def process_exception(self, request, exception):
        """
        Close database connection on exception
        """
        if connection.connection:
            connection.close()
        return None