"""
VitalBook Access Control Middleware
====================================
RULE:
  Regular users (non-staff) trying to access /admin/ are redirected to
  /admin/login/ so they can log in as admin from there.

  Admin users can freely use both portals simultaneously.
"""

from django.shortcuts import redirect


class SeparateAdminUserAccessMiddleware:
    """
    Prevents regular (non-staff) users from accessing the Django admin panel.
    Instead of showing an error, we redirect them to /admin/login/ cleanly.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = request.path

        # If a non-admin authenticated user tries to reach any /admin/ page,
        # send them to /admin/login/ so they can switch accounts.
        if path.startswith('/admin/') and path != '/admin/login/':
            user = request.user
            if user.is_authenticated and not user.is_staff and not user.is_superuser:
                return redirect('/admin/login/')

        return self.get_response(request)


class RestrictAdminMiddleware:
    """
    Acts as a total barrier for Admins trying to access the patient-facing site.
    If an admin accesses any non-admin route (except logout, media, and static), they are redirected to /admin/.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        from django.urls import reverse
        from django.conf import settings
        
        # 1. Check if the user is actually logged in and is an Admin/Staff
        if request.user.is_authenticated and (request.user.is_staff or request.user.is_superuser):
            
            # 2. Check if they are trying to access a non-admin page
            # We allow '/admin/', '/api/admin/', '/logout/', MEDIA_URL, and STATIC_URL
            if (not request.path.startswith('/admin/') and 
                not request.path.startswith('/api/admin/') and 
                not request.path.startswith(settings.MEDIA_URL) and 
                not request.path.startswith(settings.STATIC_URL) and 
                request.path != reverse('logout')):
                
                # 3. KICK THEM BACK TO THE ADMIN PANEL
                return redirect('/admin/')

        # Let normal patients proceed as usual
        return self.get_response(request)


from django.core.cache import cache
from django.utils import timezone

class UserActivityMiddleware:
    """
    Updates the 'last seen' timestamp of the user in the cache upon every request.
    This allows us to track real-time "Online/Offline" status in the Django Admin.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if hasattr(request, 'user') and request.user.is_authenticated:
            # Set cache key to last for 5 minutes (300 seconds)
            cache.set(f'seen_{request.user.username}', timezone.now(), 300)
        return self.get_response(request)
