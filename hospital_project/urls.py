"""
URL configuration for hospital_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from django.contrib.auth import logout as auth_logout
from django.shortcuts import render, redirect
from appointment.admin import admin_site

def admin_logged_out(request):
    """Premium VitalBook 'You've been signed out' page."""
    return render(request, 'admin/logged_out.html')

def custom_admin_logout(request):
    """Gracefully handle logging out via GET or POST to prevent Django 5.x 405 Method Not Allowed errors."""
    auth_logout(request)
    return redirect('/admin-logged-out/')

def preview_email(request):
    context = {
        'patient_name': 'John Doe',
        'doctor_name': 'Sarah Smith',
        'date': '24 April 2026',
        'medicines': '1. Amoxicillin 500mg - 1 tablet twice a day for 5 days\n2. Paracetamol 500mg - 1 tablet as needed for fever',
        'instructions': 'Please take the antibiotics after meals. Drink plenty of water and rest well. If symptoms persist, contact the clinic.',
    }
    return render(request, 'emails/prescription_email.html', context)

urlpatterns = [
    # Override admin logout BEFORE admin.site.urls so our custom GET/POST handler takes effect
    path('admin/logout/', custom_admin_logout, name='admin_logout_override'),
    path('admin/', admin_site.urls),
    path('admin-logged-out/', admin_logged_out, name='admin_logged_out'),
    path('preview-email/', preview_email, name='preview_email'),
    path('', include('appointment.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
