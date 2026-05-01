from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from . import api_views

# DRF router for REST API
router = DefaultRouter()
router.register(r'specializations', api_views.SpecializationViewSet, basename='specialization')
router.register(r'doctors', api_views.DoctorViewSet, basename='doctor')
router.register(r'patients', api_views.PatientViewSet, basename='patient')
router.register(r'appointments', api_views.AppointmentViewSet, basename='appointment')
router.register(r'reviews', api_views.ReviewViewSet, basename='review')

urlpatterns = [
    # REST API
    path('api/', include(router.urls)),
    path('api/auth/', include('rest_framework.urls')),

    # Main pages
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('services/', views.services, name='services'),
    path('contact/', views.contact, name='contact'),

    # Authentication
    path('register/', views.register, name='register'),
    path('verify-otp/', views.verify_otp, name='verify_otp'),
    path('resend-otp/', views.resend_otp, name='resend_otp'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('profile/', views.profile, name='profile'),

    # Patient Dashboard
    path('patient/dashboard/', views.patient_dashboard, name='patient_dashboard'),
    path('patient/profile/update/', views.update_profile, name='update_profile'),

    # Doctor Dashboard
    path('doctor/dashboard/', views.doctor_dashboard, name='doctor_dashboard'),
    path('doctor/profile/update/', views.update_doctor_profile, name='update_doctor_profile'),
    path('appointments/<int:appointment_id>/update-status/', views.update_appointment_status, name='update_appointment_status'),

    # Doctors
    path('doctors/', views.doctor_list, name='doctor_list'),
    path('doctor/<int:doctor_id>/', views.doctor_detail, name='doctor_detail'),
    path('search/', views.search_doctors, name='search_doctors'),

    # Appointments
    path('book/<int:doctor_id>/', views.book_appointment, name='book_appointment'),
    path('my-appointments/', views.my_appointments, name='my_appointments'),
    path('appointment/<int:appointment_id>/', views.appointment_detail, name='appointment_detail'),
    path('cancel/<int:appointment_id>/', views.cancel_appointment, name='cancel_appointment'),
    path('cancel/request/<int:appointment_id>/', views.request_cancellation, name='request_cancellation'),
    path('cancel/verify/<int:appointment_id>/', views.verify_cancellation_payment, name='verify_cancellation_payment'),
    path('reschedule/<int:appointment_id>/', views.reschedule_appointment, name='reschedule_appointment'),

    # Reviews
    path('review/<int:appointment_id>/', views.add_review, name='add_review'),
    path('review/submit/<int:appointment_id>/', views.submit_review, name='submit_review'),
    path('doctor/<int:doctor_id>/reviews/', views.doctor_reviews, name='doctor_reviews'),

    # Payment — Cashfree UPI
    path('checkout/<int:appointment_id>/', views.checkout, name='checkout'),
    path('payment/process/', views.process_payment, name='process_payment'),
    path('payment-success/<int:appointment_id>/', views.payment_success, name='payment_success'),
    path('payment/verify/', views.verify_payment, name='verify_payment'),
    path('payment/webhook/', views.payment_webhook, name='payment_webhook'),
    path('payment/receipt/<int:appointment_id>/', views.payment_receipt, name='payment_receipt'),
    path('payment/failed/', views.payment_failed, name='payment_failed'),

    # Prescription PDF Download / View
    path('patient/prescriptions/<int:appointment_id>/', views.view_prescription, name='view_prescription'),
    path('prescription/<int:appointment_id>/download/', views.download_prescription_pdf, name='download_prescription'),

    # Admin quick-action URLs (staff-only, used by AppointmentAdmin action buttons)
    path('appointments/<int:appointment_id>/confirm-admin/', views.confirm_appointment_admin, name='confirm_appointment_admin'),
    path('appointments/<int:appointment_id>/cancel-admin/',  views.cancel_appointment_admin,  name='cancel_appointment_admin'),
    path('appointments/<int:appointment_id>/complete-admin/', views.complete_appointment_admin, name='complete_appointment_admin'),

    # Admin dashboard approval workflow (redirects back to admin:index)
    path('appointments/<int:appointment_id>/dashboard-approve/', views.admin_approve_appointment, name='admin_approve_appointment'),
    path('appointments/<int:appointment_id>/dashboard-cancel/',  views.admin_cancel_appointment,  name='admin_cancel_appointment'),
    path('api/admin/appointment/<int:appointment_id>/details/', views.admin_appointment_details, name='admin_appointment_details'),

    # Medical Records
    path('medical-records/upload/', views.upload_medical_record, name='upload_medical_record'),
    path('medical-records/delete/<int:record_id>/', views.delete_medical_record, name='delete_medical_record'),

    # AJAX endpoints
    path('ajax/load-slots/', views.ajax_load_slots, name='ajax_load_slots'),
]
