from django.contrib import auth
from django.utils import timezone
import datetime

class SessionTimeoutMiddleware:
    """
    Middleware that tracks user activity and expires sessions after a period of inactivity.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Process request first so we can ensure response is okay
        response = self.get_response(request)
        
        # Only track activity for authenticated users
        if request.user.is_authenticated:
            try:
                # Get the last activity time from the session
                last_activity = request.session.get('last_activity')
                
                # Check if the session has been inactive for too long
                if last_activity:
                    try:
                        last_activity = datetime.datetime.fromisoformat(last_activity)
                        # Convert to aware datetime if it's naive
                        if last_activity.tzinfo is None:
                            last_activity = timezone.make_aware(last_activity)
                            
                        now = timezone.now()
                        inactive_time = now - last_activity
                        
                        # If the user has been inactive for more than the session timeout,
                        # log them out (30 minutes in seconds = 1800)
                        if inactive_time.total_seconds() > 1800:
                            auth.logout(request)
                    except (ValueError, TypeError) as e:
                        # If there's an error parsing the datetime, just update it
                        pass
                
                # Update the last activity time
                request.session['last_activity'] = timezone.now().isoformat()
            except Exception:
                # Ensure we don't break the application if there's an error
                pass
                
        return response