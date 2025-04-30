from django.contrib import auth
from django.utils import timezone

class SessionTimeoutMiddleware:
    """
    Middleware that tracks user activity and expires sessions after a period of inactivity.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            # Get the last activity time from the session
            last_activity = request.session.get('last_activity')
            
            # Check if the session has been inactive for too long
            if last_activity:
                last_activity = timezone.datetime.fromisoformat(last_activity)
                inactive_time = timezone.now() - last_activity
                
                # If the user has been inactive for more than the session timeout,
                # log them out (30 minutes in seconds = 1800)
                if inactive_time.total_seconds() > 1800:
                    auth.logout(request)
            
            # Update the last activity time
            request.session['last_activity'] = timezone.now().isoformat()
        
        response = self.get_response(request)
        return response