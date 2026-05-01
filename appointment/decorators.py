from django.shortcuts import redirect
from django.contrib import messages
from functools import wraps

def patient_required(view_func):
    """
    This gatekeeper checks if the user is an Admin or Staff. 
    If they are, it kicks them out of Patient-only views.
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        # If the user is an Admin or Staff member
        if request.user.is_staff or request.user.is_superuser:
            messages.error(request, "⚠️ Admins and Staff cannot access patient booking pages. Redirected to Admin Panel.")
            # Send them back to their own territory!
            return redirect('/admin/') 
            
        # If they are a normal patient, let them pass
        return view_func(request, *args, **kwargs)
        
    return wrapper
