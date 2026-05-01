from django.contrib import admin
from django.contrib.admin import AdminSite
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models import Sum
from .models import Doctor, Patient, Appointment, Specialization, Review, ContactMessage, Billing, Prescription, Payment, OTPVerification, MedicalRecord


# ── Custom Admin Site with Real-Time Daily Stats ─────────────────────────────
class VitalBookAdminSite(AdminSite):
    """Custom admin site that injects daily KPI stats into the index page."""
    site_header = 'VitalBook Administration'
    site_title = 'VitalBook Admin'
    index_title = 'Dashboard'
    index_template = 'admin/index.html'

    def index(self, request, extra_context=None):
        local_now = timezone.localtime(timezone.now())
        today = local_now.date()

        # The user's requested logic adapted for our models
        paid_appt_ids = Payment.objects.filter(payment_status='Completed').values_list('appointment_id', flat=True)

        todays_appts = Appointment.objects.filter(date=today).count()
        pending = Appointment.objects.filter(status='Pending').count()
        confirmed = Appointment.objects.filter(status='Confirmed').count()
        
        today_revenue = Payment.objects.filter(
            payment_status='Completed',
            appointment__date=today
        ).aggregate(total=Sum('amount'))['total'] or 0

        total_patients = Patient.objects.count()
        total_appointments = Appointment.objects.count()
        total_doctors = Doctor.objects.count()
        
        total_revenue = Payment.objects.filter(
            payment_status='Completed'
        ).aggregate(total=Sum('amount'))['total'] or 0

        # Approval workflow — oldest 10 Pending appointments awaiting admin action
        pending_approvals = (
            Appointment.objects
            .filter(status='Pending')
            .select_related('patient', 'doctor', 'doctor__specialization')
            .order_by('date', 'time')[:10]
        )

        # Build a time-based greeting
        hour = local_now.hour
        if hour < 12:
            greeting = 'Good Morning'
        elif hour < 17:
            greeting = 'Good Afternoon'
        else:
            greeting = 'Good Evening'

        extra_context = extra_context or {}
        extra_context.update({
            # Keys matched exactly to what index.html template expects
            'greeting': greeting,
            'todays_appts': todays_appts,
            'pending_appts': pending,
            'confirmed_appts': confirmed,
            'todays_revenue': today_revenue,
            'total_patients': total_patients,
            'total_appointments': total_appointments,
            'total_doctors': total_doctors,
            'total_revenue': total_revenue,
            'pending_approvals': pending_approvals,
        })
        return super().index(request, extra_context)

    def app_index(self, request, app_label, extra_context=None):
        """Redirect ALL app index pages back to the main dashboard.
        This removes /admin/appointment/ and /admin/auth/ etc."""
        from django.shortcuts import redirect
        return redirect('/admin/')

    def get_urls(self):
        from django.urls import path
        urls = super().get_urls()
        custom_urls = [
            path(
                'dashboard-approve/<int:appointment_id>/',
                self.admin_view(self.dashboard_approve_view),
                name='dashboard_approve_appointment',
            ),
            path(
                'dashboard-cancel/<int:appointment_id>/',
                self.admin_view(self.dashboard_cancel_view),
                name='dashboard_cancel_appointment',
            ),
        ]
        return custom_urls + urls

    def dashboard_approve_view(self, request, appointment_id):
        """Approve (Confirm) a Pending appointment from the dashboard widget."""
        from django.contrib import messages as msg
        from django.shortcuts import get_object_or_404, redirect
        from . import email_utils

        appointment = get_object_or_404(Appointment, id=appointment_id)
        if appointment.status != 'Pending':
            msg.warning(
                request,
                f'⚠️ Appointment #{appointment.id} is already {appointment.status}.'
            )
            return redirect('/admin/')

        appointment.status = 'Confirmed'
        appointment.save()
        try:
            email_utils.send_appointment_confirmation(appointment)
        except Exception:
            pass

        msg.success(
            request,
            f'✅ Appointment #{appointment.id} for {appointment.patient.name} '
            f'with Dr. {appointment.doctor.name} confirmed. Patient notified.'
        )
        return redirect('/admin/')

    def dashboard_cancel_view(self, request, appointment_id):
        """Cancel a Pending appointment from the dashboard widget."""
        from django.contrib import messages as msg
        from django.shortcuts import get_object_or_404, redirect
        from django.utils import timezone as tz
        from . import email_utils

        appointment = get_object_or_404(Appointment, id=appointment_id)
        if appointment.status not in ('Pending', 'Confirmed'):
            msg.warning(
                request,
                f'⚠️ Appointment #{appointment.id} is already {appointment.status}.'
            )
            return redirect('/admin/')

        appointment.status = 'Cancelled'
        appointment.cancelled_at = tz.now()
        appointment.save()
        try:
            email_utils.send_appointment_cancelled(appointment, cancelled_by='admin')
        except Exception:
            pass

        msg.warning(
            request,
            f'❌ Appointment #{appointment.id} for {appointment.patient.name} cancelled.'
        )
        return redirect('/admin/')


# Instantiate the custom admin site
admin_site = VitalBookAdminSite(name='vitalbook_admin')


# ── Model Registrations on Custom Admin Site ─────────────────────────────────

class AllowCustomFiltersMixin:
    """Mixin to allow custom URL queries that Django blocks by default in 2.1+"""
    def lookup_allowed(self, lookup, value, request=None, **kwargs):
        # Allow your custom URL parameters to bypass Django's strict filter security
        allowed_lookups = [
            'is_paid', 
            'status', 
            'date_from', 
            'date_to', 
            'payment', 
            'specialization', 
            # 👇 Added 'specialization__name' to the safe list
            'specialization__name',
            
            # (Kept these intact so your other date filters don't crash)
            'created_at__gte', 'created_at__lte', 'date__gte', 'date__lte'
        ]
        
        if lookup in allowed_lookups:
            return True
            
        # Pass the request along to the parent class
        return super().lookup_allowed(lookup, value, request=request, **kwargs)


class SpecializationAdmin(admin.ModelAdmin):
    list_display = ['name', 'icon']
    search_fields = ['name']
admin_site.register(Specialization, SpecializationAdmin)


from .models import Availability

class AvailabilityInline(admin.TabularInline):
    model = Availability
    extra = 1

class DoctorAdmin(AllowCustomFiltersMixin, admin.ModelAdmin):
    inlines = [AvailabilityInline]
    list_display = ['name', 'designation', 'specialization', 'experience_years', 'consultation_fee', 'rating', 'is_available_display', 'phone']
    search_fields = ['name', 'email', 'phone']
    list_editable = ['rating']
    list_filter = ['designation', 'specialization', 'is_available']
    sortable_by = ()
    ordering = ['experience_years']
    fieldsets = (
        ('Personal Information', {
            'fields': ('name', 'email', 'phone', 'image')
        }),
        ('Professional Details', {
            'fields': ('specialization', 'qualification', 'designation', 'experience_years', 'bio', 'rating')
        }),
        ('Availability', {
            'fields': ('available_days', 'available_time', 'is_available')
        }),
        ('Financial', {
            'fields': ('consultation_fee',)
        }),
    )

    def is_available_display(self, obj):
        from django.utils.html import format_html
        if obj.is_available:
            return format_html('<span style="color:#28a745;font-weight:bold;">{}</span>', 'Available')
        return format_html('<span style="color:#dc3545;font-weight:bold;">{}</span>', 'Not Available')
    is_available_display.short_description = 'Available Type'
admin_site.register(Doctor, DoctorAdmin)


class PatientAdmin(AllowCustomFiltersMixin, admin.ModelAdmin):
    list_display = ['name', 'email', 'phone', 'date_of_birth', 'age_display', 'gender', 'blood_group', 'created_at']
    search_fields = ['name', 'email', 'phone']
    sortable_by = ()
    fieldsets = (
        ('Personal Information', {
            'fields': ('user', 'name', 'email', 'phone', 'date_of_birth', 'gender', 'blood_group')
        }),
        ('Contact Details', {
            'fields': ('address', 'emergency_contact')
        }),
        ('Medical Information', {
            'fields': ('medical_history',)
        }),
    )

    def age_display(self, obj):
        age = obj.age
        return f'{age} yrs' if age is not None else '—'
    age_display.short_description = 'Age'
admin_site.register(Patient, PatientAdmin)


class PaidPendingFilter(admin.SimpleListFilter):
    """Custom filter: shows appointments that are PAID but not yet Confirmed."""
    title = '💳 Payment & Confirmation'
    parameter_name = 'paid_status'

    def lookups(self, request, model_admin):
        return [
            ('paid_pending',  '🔔 Paid — Awaiting Confirmation'),
            ('paid_confirmed','✅ Paid & Confirmed'),
            ('unpaid',        '❌ Unpaid'),
        ]

    def queryset(self, request, queryset):
        paid_ids = Payment.objects.filter(
            payment_status='Completed'
        ).values_list('appointment_id', flat=True)

        if self.value() == 'paid_pending':
            return queryset.filter(id__in=paid_ids, status='Pending')
        if self.value() == 'paid_confirmed':
            return queryset.filter(id__in=paid_ids, status='Confirmed')
        if self.value() == 'unpaid':
            return queryset.exclude(id__in=paid_ids)
        return queryset


class AppointmentAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'patient_name', 'doctor_name',
        'date', 'time', 'status_badge',
        'payment_status_display', 'action_buttons'
    ]
    search_fields = ['patient__user__username', 'patient__name', 'doctor__name']
    ordering = ['-date', '-time']
    sortable_by = ['patient_name', 'doctor_name', 'status_badge', 'payment_status_display']

    def get_queryset(self, request):
        """Filter appointments using 5 clean URL params from the filter modal."""
        from django.utils.dateparse import parse_date
        qs = super().get_queryset(request)

        status         = request.GET.get('status', '').strip()
        specialization = request.GET.get('specialization', '').strip()
        date_from      = request.GET.get('date_from', '').strip()
        date_to        = request.GET.get('date_to', '').strip()
        payment        = request.GET.get('payment', '').strip()

        if status and status != 'All':
            qs = qs.filter(status=status)

        if specialization and specialization != 'All':
            qs = qs.filter(doctor__specialization__name=specialization)

        if date_from:
            parsed = parse_date(date_from)
            if parsed:
                qs = qs.filter(date__gte=parsed)

        if date_to:
            parsed = parse_date(date_to)
            if parsed:
                qs = qs.filter(date__lte=parsed)

        if payment == 'paid':
            qs = qs.filter(payments__payment_status='Completed').distinct()
        elif payment == 'unpaid':
            paid_ids = Payment.objects.filter(
                payment_status='Completed'
            ).values_list('appointment_id', flat=True)
            qs = qs.exclude(id__in=paid_ids)

        return qs


    def changelist_view(self, request, extra_context=None):
        """Process action=confirm|cancel|complete&id=X query params."""
        action = request.GET.get('action')
        appt_id = request.GET.get('id')
        if action and appt_id:
            try:
                appt = Appointment.objects.get(id=appt_id)
                if action == 'confirm' and appt.status == 'Pending':
                    appt.status = 'Confirmed'
                    appt.save()
                    try:
                        from . import email_utils
                        email_utils.send_appointment_confirmation(appt)
                    except Exception:
                        pass
                    self.message_user(request, f'✅ Appointment #{appt.id} for {appt.patient.name} confirmed. Patient notified.', level='success')
                elif action == 'cancel':
                    appt.status = 'Cancelled'
                    appt.save()
                    self.message_user(request, f'❌ Appointment #{appt.id} cancelled.', level='warning')
                elif action == 'complete' and appt.status == 'Confirmed':
                    appt.status = 'Completed'
                    appt.save()
                    self.message_user(request, f'🏁 Appointment #{appt.id} marked as completed.', level='info')
                else:
                    self.message_user(request, f'⚠️ Action "{action}" not allowed for current status.', level='warning')
            except Appointment.DoesNotExist:
                self.message_user(request, '⚠️ Appointment not found.', level='error')
            # Redirect to clean URL (removes action params)
            from django.shortcuts import redirect
            return redirect('/admin/appointment/appointment/')
        return super().changelist_view(request, extra_context)

    def patient_name(self, obj):
        return obj.patient.name
    patient_name.short_description = 'Patient'

    def doctor_name(self, obj):
        return obj.doctor.name
    doctor_name.short_description = 'Doctor'

    def status_badge(self, obj):
        from django.utils.html import format_html
        if obj.status == 'Confirmed':
            return format_html('<span class="saas-badge badge-success">{}</span>', 'Confirmed')
        elif obj.status == 'Cancelled':
            return format_html('<span class="saas-badge badge-danger">{}</span>', 'Cancelled')
        elif obj.status == 'Pending':
            return format_html('<span class="saas-badge badge-warning">{}</span>', 'Pending')
        elif obj.status == 'Completed':
            return format_html('<span class="saas-badge badge-info">{}</span>', 'Completed')
        return format_html('<span class="saas-badge badge-neutral">{}</span>', obj.status)
    status_badge.short_description = 'Status'

    def payment_status_display(self, obj):
        from django.utils.html import format_html
        has_payment = obj.payments.filter(payment_status='Completed').exists()
        if has_payment:
            return format_html('<span class="payment-status text-success"><i class="fas fa-check-circle"></i> {}</span>', 'Paid')
        return format_html('<span class="payment-status text-danger"><i class="fas fa-times-circle"></i> {}</span>', 'Unpaid')
    payment_status_display.short_description = 'Payment'

    def action_buttons(self, obj):
        """One-click action buttons shown per row in the changelist."""
        from django.utils.html import format_html
        is_paid = obj.payments.filter(payment_status='Completed').exists()

        if obj.status == 'Pending':
            if is_paid:
                return format_html(
                    '<a href="/admin/appointment/appointment/?action=confirm&id={}" '
                    'style="background:#28a745;color:white;padding:5px 12px;'
                    'border-radius:6px;text-decoration:none;font-size:12px;'
                    'font-weight:600;box-shadow:0 2px 4px rgba(0,0,0,.2);">'
                    '✅ Confirm</a>&nbsp;'
                    '<a href="/admin/appointment/appointment/?action=cancel&id={}" '
                    'style="background:#dc3545;color:white;padding:5px 10px;'
                    'border-radius:6px;text-decoration:none;font-size:12px;">'
                    '❌ Cancel</a>',
                    obj.id, obj.id
                )
            # Pending but unpaid — allow editing or cancel
            return format_html(
                '<a href="/admin/appointment/appointment/{}/change/" '
                'style="background:#ffc107;color:#333;padding:5px 12px;'
                'border-radius:6px;text-decoration:none;font-size:12px;'
                'font-weight:600;">✏️ Edit</a>&nbsp;'
                '<a href="/admin/appointment/appointment/?action=cancel&id={}" '
                'style="background:#dc3545;color:white;padding:5px 10px;'
                'border-radius:6px;text-decoration:none;font-size:12px;">'
                '❌ Cancel</a>',
                obj.id, obj.id
            )

        if obj.status == 'Confirmed':
            return format_html(
                '<a href="/admin/appointment/appointment/?action=complete&id={}" '
                'class="action-btn-complete">'
                '<i class="fas fa-check-circle"></i> Complete</a>',
                obj.id
            )

        return format_html(
            '<span style="color:#6c757d;font-size:12px;font-style:italic;">{}</span>',
            obj.status
        )
    action_buttons.short_description = 'Action'

    # ── Bulk admin actions ────────────────────────────────────────────────────
    actions = [
        'confirm_paid_appointments',
        'confirm_appointments',
        'cancel_appointments',
        'mark_completed',
    ]

    @admin.action(description='Confirm PAID appointments & notify patients')
    def confirm_paid_appointments(self, request, queryset):
        """Only confirms appointments where payment is completed, then emails patients."""
        from . import email_utils
        paid_pending = queryset.filter(status='Pending').filter(
            payments__payment_status='Completed'
        ).distinct()
        count = 0
        for appt in paid_pending:
            appt.status = 'Confirmed'
            appt.save()
            try:
                email_utils.send_appointment_confirmation(appt)
            except Exception:
                pass
            count += 1
        self.message_user(
            request,
            f'✅ {count} paid appointment(s) confirmed. Patients have been notified by email.',
            level='success' if count else 'warning'
        )

    @admin.action(description='Confirm selected appointments (regardless of payment)')
    def confirm_appointments(self, request, queryset):
        from . import email_utils
        updated = queryset.exclude(status__in=['Confirmed', 'Completed']).update(status='Confirmed')
        self.message_user(request, f'{updated} appointment(s) confirmed.')

    @admin.action(description='Cancel selected appointments')
    def cancel_appointments(self, request, queryset):
        updated = queryset.exclude(status='Cancelled').update(status='Cancelled')
        self.message_user(request, f'{updated} appointments cancelled.')

    @admin.action(description='Mark as Completed')
    def mark_completed(self, request, queryset):
        updated = queryset.filter(status='Confirmed').update(status='Completed')
        self.message_user(request, f'{updated} appointments marked as completed.')

    fieldsets = (
        ('Appointment Details', {
            'fields': ('patient', 'doctor', 'date', 'time', 'status')
        }),
        ('Patient Information', {
            'fields': ('reason', 'symptoms')
        }),
        ('Doctor Notes', {
            'fields': ('notes', 'prescription')
        }),
        ('Cancellation & QR', {
            'fields': ('cancellation_fee_applied', 'cancelled_at', 'qr_code'),
            'classes': ('collapse',),
        }),
    )
    readonly_fields = ['created_at', 'updated_at', 'cancelled_at']

    # ── Custom URLs ───────────────────────────────────────────────────────────
    def get_urls(self):
        from django.urls import path
        urls = super().get_urls()
        custom_urls = [
            path(
                'pending-count/',
                self.admin_site.admin_view(self.pending_count_view),
                name='appointment_pending_count'
            ),
            path(
                'quick-confirm/<int:appointment_id>/',
                self.admin_site.admin_view(self.quick_confirm_view),
                name='appointment_quick_confirm'
            ),
            path(
                'admin-stats/',
                self.admin_site.admin_view(self.admin_stats_view),
                name='appointment_admin_stats'
            ),
        ]
        return custom_urls + urls

    def admin_stats_view(self, request):
        """JSON: KPI metrics for the admin dashboard."""
        from django.http import JsonResponse
        from django.utils import timezone
        from datetime import timedelta, date

        today = date.today()
        week_ago = today - timedelta(days=6)

        # KPI counts
        today_count    = Appointment.objects.filter(date=today).count()
        pending_count  = Appointment.objects.filter(status='Pending').count()
        week_patients  = Patient.objects.filter(created_at__date__gte=week_ago).count()
        month_revenue  = Payment.objects.filter(
            payment_status='Completed',
            payment_date__month=today.month,
            payment_date__year=today.year,
        ).aggregate(total=__import__('django.db.models', fromlist=['Sum']).Sum('amount'))['total'] or 0

        # Last 7 days chart — appointments per day
        days_labels, days_data = [], []
        for i in range(6, -1, -1):
            d = today - timedelta(days=i)
            days_labels.append(d.strftime('%a'))
            days_data.append(Appointment.objects.filter(date=d).count())

        # Specialization doughnut
        from django.db.models import Count
        spec_qs = (
            Appointment.objects
            .values('doctor__specialization__name')
            .annotate(cnt=Count('id'))
            .order_by('-cnt')[:6]
        )
        spec_labels = [x['doctor__specialization__name'] or 'Other' for x in spec_qs]
        spec_data   = [x['cnt'] for x in spec_qs]

        return JsonResponse({
            'kpi': {
                'today':       today_count,
                'pending':     pending_count,
                'new_patients': week_patients,
                'revenue':     float(month_revenue),
            },
            'chart_days': {'labels': days_labels, 'data': days_data},
            'chart_spec':  {'labels': spec_labels,  'data': spec_data},
        })

    def pending_count_view(self, request):
        """JSON: count + list of PAID Pending appointments for admin notification bar."""
        from django.http import JsonResponse
        paid_ids = set(
            Payment.objects.filter(
                payment_status='Completed'
            ).values_list('appointment_id', flat=True)
        )
        pending = Appointment.objects.filter(
            status='Pending'
        ).select_related('patient', 'doctor').order_by('date', 'time')
        # Filter to only paid pending
        paid_pending = [a for a in pending if a.id in paid_ids]
        data = {
            'count': len(paid_pending),
            'appointments': [
                {
                    'id': a.id,
                    'patient': a.patient.name,
                    'doctor': a.doctor.name,
                    'specialization': a.doctor.specialization.name if a.doctor.specialization else '',
                    'date': a.date.strftime('%d %b %Y'),
                    'time': a.time.strftime('%I:%M %p'),
                    'is_paid': True,
                    'confirm_url': f'/admin/appointment/appointment/quick-confirm/{a.id}/',
                    'detail_url':  f'/admin/appointment/appointment/{a.id}/change/',
                }
                for a in paid_pending[:15]
            ]
        }
        return JsonResponse(data)

    def quick_confirm_view(self, request, appointment_id):
        """One-click confirm: marks Pending→Confirmed and emails the patient."""
        from django.http import JsonResponse
        from django.contrib import messages as django_messages

        # Detect AJAX calls by X-Requested-With header (set by fetch/jQuery)
        is_ajax = request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'

        try:
            appt = Appointment.objects.get(id=appointment_id, status='Pending')
            appt.status = 'Confirmed'
            appt.save()

            # Notify patient by email
            try:
                from . import email_utils
                email_utils.send_appointment_confirmation(appt)
            except Exception:
                pass

            remaining = Appointment.objects.filter(status='Pending').count()

            if is_ajax:
                # Called from dashboard JS widget — return JSON
                return JsonResponse({'success': True, 'remaining': remaining})
            else:
                # Called by clicking the link in the admin list — redirect with message
                from django.shortcuts import redirect
                django_messages.success(
                    request,
                    f'✅ Appointment #{appt.id} for {appt.patient.name} confirmed. Patient notified by email.'
                )
                return redirect('/admin/appointment/appointment/?status__exact=Pending')

        except Appointment.DoesNotExist:
            if is_ajax:
                return JsonResponse(
                    {'success': False, 'error': 'Not found or already confirmed'}, status=404
                )
            from django.shortcuts import redirect
            django_messages.warning(request, '⚠️ Appointment not found or already confirmed.')
            return redirect('/admin/appointment/appointment/')


admin_site.register(Appointment, AppointmentAdmin)


class BillingAdmin(AllowCustomFiltersMixin, admin.ModelAdmin):
    list_display = ['appointment', 'doctor_specialization', 'billing_type', 'total_amount', 'is_paid_display', 'created_at']
    search_fields = ['appointment__patient__name', 'appointment__doctor__name']
    readonly_fields = ['created_at']
    sortable_by = ()

    def doctor_specialization(self, obj):
        if obj.appointment and obj.appointment.doctor and obj.appointment.doctor.specialization:
            return obj.appointment.doctor.specialization.name
        return "General Practice"
    doctor_specialization.short_description = 'Specialization'

    def is_paid_display(self, obj):
        from django.utils.html import format_html
        if obj.is_paid:
            return format_html('<span class="payment-status text-success" style="color:#28a745;font-weight:bold;"><i class="fas fa-check-circle"></i> {}</span>', 'Paid')
        return format_html('<span class="payment-status text-danger" style="color:#dc3545;font-weight:bold;"><i class="fas fa-times-circle"></i> {}</span>', 'Unpaid')
    is_paid_display.short_description = 'Is Paid'
admin_site.register(Billing, BillingAdmin)


class PrescriptionAdmin(admin.ModelAdmin):
    list_display = ['patient_name', 'doctor_name', 'appointment_date', 'issued_on']
    search_fields = ['appointment__patient__name', 'appointment__doctor__name', 'medicines']
    readonly_fields = ['issued_on']
    sortable_by = ()

    class Media:
        js = ('appointment/js/admin_prescription.js',)

    def patient_name(self, obj):
        return obj.appointment.patient.name
    patient_name.short_description = 'Patient'

    def doctor_name(self, obj):
        return f"Dr. {obj.appointment.doctor.name}"
    doctor_name.short_description = 'Doctor'

    def appointment_date(self, obj):
        return obj.appointment.date
    appointment_date.short_description = 'Appointment Date'
    appointment_date.admin_order_field = 'appointment__date'

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """
        Filter the Appointment dropdown to show only Completed appointments
        that also have a completed payment — the only ones eligible for prescriptions.
        Note: Appointment has no direct payment_status field; payments are on the
        related Payment model via appointment.payments.
        """
        if db_field.name == "appointment":
            paid_appt_ids = Payment.objects.filter(
                payment_status='Completed'
            ).values_list('appointment_id', flat=True)

            kwargs["queryset"] = Appointment.objects.filter(
                status='Completed',
                id__in=paid_appt_ids
            ).select_related('patient', 'doctor').order_by('-date')
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

admin_site.register(Prescription, PrescriptionAdmin)


class ReviewAdmin(AllowCustomFiltersMixin, admin.ModelAdmin):
    list_display = ('doctor', 'patient', 'rating', 'appointment', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('doctor__name', 'patient__name')
    readonly_fields = ('created_at',)
    sortable_by = ()
    fieldsets = (
        ('Review Details', {
            'fields': ('doctor', 'patient', 'appointment', 'rating', 'comment')
        }),
        ('Metadata', {
            'fields': ('created_at',),
        }),
    )
admin_site.register(Review, ReviewAdmin)


class ContactMessageAdmin(AllowCustomFiltersMixin, admin.ModelAdmin):
    list_display = ['name', 'email', 'subject', 'message_preview', 'is_read_display', 'created_at']
    search_fields = ['name', 'email', 'subject', 'message']
    readonly_fields = ['created_at']
    list_filter = ['is_read', 'created_at']
    sortable_by = ()
    actions = ['mark_as_read', 'mark_as_unread']

    def message_preview(self, obj):
        from django.utils.html import format_html
        # Truncate message to 75 characters
        msg = obj.message
        if len(msg) > 75:
            msg = msg[:75] + '...'
        return msg
    message_preview.short_description = 'Message Preview'

    def is_read_display(self, obj):
        from django.utils.html import format_html
        if obj.is_read:
            return format_html('<span style="color:#28a745;font-weight:bold;">{}</span>', 'Read')
        return format_html('<span style="color:#dc3545;font-weight:bold;">{}</span>', 'Unread')
    is_read_display.short_description = 'Status'

    @admin.action(description='Mark selected messages as Read')
    def mark_as_read(self, request, queryset):
        updated = queryset.update(is_read=True)
        self.message_user(request, f'{updated} message(s) marked as read.')

    @admin.action(description='Mark selected messages as Unread')
    def mark_as_unread(self, request, queryset):
        updated = queryset.update(is_read=False)
        self.message_user(request, f'{updated} message(s) marked as unread.')

admin_site.register(ContactMessage, ContactMessageAdmin)


class PaymentAdmin(AllowCustomFiltersMixin, admin.ModelAdmin):
    list_display = [
        'transaction_id', 'patient_name', 'doctor_name',
        'amount', 'payment_status', 'payment_method',
        'appointment_status_display', 'confirm_button', 'payment_date',
    ]
    search_fields = ['transaction_id', 'appointment__patient__name', 'appointment__doctor__name']
    readonly_fields = ['transaction_id', 'created_at', 'payment_date']
    ordering = ['-created_at']

    def patient_name(self, obj):
        return obj.appointment.patient.name
    patient_name.short_description = 'Patient'

    def doctor_name(self, obj):
        return obj.appointment.doctor.name
    doctor_name.short_description = 'Doctor'

    def appointment_status_display(self, obj):
        from django.utils.html import format_html
        status = obj.appointment.status
        colors = {
            'Pending':   '#ffc107',
            'Confirmed': '#28a745',
            'Completed': '#0d6efd',
            'Cancelled': '#dc3545',
        }
        color = colors.get(status, '#6c757d')
        return format_html(
            '<span style="background:{};color:white;padding:3px 8px;'
            'border-radius:20px;font-size:11px;font-weight:600;">{}</span>',
            color, status
        )
    appointment_status_display.short_description = 'Appt. Status'

    def confirm_button(self, obj):
        """Show a Confirm button if payment is complete but appointment is still Pending."""
        from django.utils.html import format_html
        if obj.payment_status == 'Completed' and obj.appointment.status == 'Pending':
            return format_html(
                '<a href="/admin/appointment/appointment/quick-confirm/{}/" '
                'style="background:#28a745;color:white;padding:4px 12px;'
                'border-radius:6px;text-decoration:none;font-size:12px;font-weight:600;">'
                '✅ Confirm Appt.</a>',
                obj.appointment.id
            )
        if obj.appointment.status == 'Confirmed':
            return format_html('<span style="color:#28a745;font-size:12px;">✔ Already Confirmed</span>')
        return format_html('<span style="color:#6c757d;font-size:12px;">—</span>')
    confirm_button.short_description = 'Action'

    fieldsets = (
        ('Payment Information', {
            'fields': ('appointment', 'amount', 'transaction_id')
        }),
        ('Status & Method', {
            'fields': ('payment_status', 'payment_method', 'payment_date')
        }),
    )
admin_site.register(Payment, PaymentAdmin)


class OTPVerificationAdmin(admin.ModelAdmin):
    list_display = ['user', 'otp', 'otp_type', 'is_verified', 'is_expired_display', 'created_at', 'expires_at']
    search_fields = ['user__username', 'user__email', 'otp']
    readonly_fields = ['created_at', 'expires_at']

    def save_model(self, request, obj, form, change):
        """Auto-set expires_at (10 min from now) if not already set."""
        from django.utils import timezone
        from datetime import timedelta
        if not obj.expires_at:
            obj.expires_at = timezone.now() + timedelta(minutes=10)
        super().save_model(request, obj, form, change)

    def is_expired_display(self, obj):
        from django.utils.html import format_html
        if obj.is_expired():
            return format_html('<span style="color:#dc3545;font-weight:600;">❌ Expired</span>')
        return format_html('<span style="color:#28a745;font-weight:600;">✅ Valid</span>')
    is_expired_display.short_description = 'Status'
admin_site.register(OTPVerification, OTPVerificationAdmin)

class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'staff_status_display')
    sortable_by = ()

    # Organize fields into cards with uppercase titles
    fieldsets = (
        ('🔒 ACCOUNT CREDENTIALS', {
            'fields': ('username', 'password'),
        }),
        ('👤 PERSONAL INFORMATION', {
            'fields': (('first_name', 'last_name'), 'email'),
        }),
        ('📅 IMPORTANT DATES', {
            'fields': (('last_login', 'date_joined'),),
        }),
    )

    # Link your custom CSS file — ?v=3.0 forces browser to bypass cache
    class Media:
        js = []
        css = {
            'all': ('css/admin_custom.css?v=3.0',)
        }

    def changelist_view(self, request, extra_context=None):
        return super().changelist_view(request, extra_context)

    def staff_status_display(self, obj):
        from django.utils.html import format_html
        
        # If user is a doctor, base status on their scheduled availability
        if hasattr(obj, 'doctor_profile') and obj.doctor_profile:
            is_online = obj.doctor_profile.is_currently_available
        else:
            # For non-doctors (e.g. patients, admins), check session activity
            from django.core.cache import cache
            is_online = cache.get(f'seen_{obj.username}') is not None

        if is_online:
            return format_html('<div style="display:flex;align-items:center;"><span class="status-indicator status-online"></span><span style="color:#10b981;font-weight:bold;">{}</span></div>', 'Active')
        return format_html('<div style="display:flex;align-items:center;"><span class="status-indicator status-busy"></span><span style="color:#ef4444;opacity:0.8;font-weight:bold;">{}</span></div>', 'Offline')
    staff_status_display.short_description = 'Login Status'

    def render_change_form(self, request, context, *args, **kwargs):
        """
        Inject Anti-Gravity inline CSS directly into the Change User page.
        This is the 'Hammer Method' — guarantees styles load even if the
        static CSS file is cached by the browser.
        """
        from django.utils.safestring import mark_safe
        anti_gravity_css = """
        <style>
            /* 1. LAYOUT & CARD DESIGN */
            #content {
                width: 95% !important;
                max-width: 1400px !important;
                margin: 0 auto !important;
                background: #0b1523 !important;
            }
            fieldset.module {
                background: #0f1c2e !important;
                border: 1px solid #1e293b !important;
                border-radius: 12px !important;
                margin-bottom: 30px !important;
                overflow: hidden !important;
            }
            .module h2 {
                background: #1a2a40 !important;
                color: #ff6b00 !important;
                padding: 15px 25px !important;
                font-size: 0.9rem !important;
                letter-spacing: 1px !important;
                text-transform: uppercase !important;
            }

            /* 2. THE ALIGNMENT FIX — Flex rows with fixed label column */
            .form-row {
                display: flex !important;
                align-items: center !important;
                padding: 20px 30px !important;
                border-bottom: 1px solid #1a2a3a !important;
            }
            .form-row label {
                flex: 0 0 180px !important;
                color: #94a3b8 !important;
                font-weight: 600 !important;
                text-transform: uppercase !important;
                font-size: 0.75rem !important;
                letter-spacing: 0.8px !important;
            }
            .form-row input[type="text"],
            .form-row input[type="email"],
            .form-row input[type="password"],
            .form-row select,
            .form-row .readonly {
                background: #162436 !important;
                border: 1px solid #2d3e50 !important;
                color: white !important;
                padding: 10px 15px !important;
                border-radius: 8px !important;
                max-width: 500px !important;
                flex: 1 !important;
            }
            .form-row input:focus {
                border-color: #ff6b00 !important;
                box-shadow: 0 0 0 4px rgba(255, 107, 0, 0.15) !important;
                outline: none !important;
            }

            /* 3. MASKING THE PASSWORD HASH */
            .field-password .readonly {
                font-size: 0 !important;
                border: none !important;
                background: transparent !important;
            }
            .field-password .readonly::before {
                content: "••••••••••••";
                font-size: 18px !important;
                color: #ff6b00 !important;
                letter-spacing: 4px !important;
                margin-right: 15px !important;
                vertical-align: middle !important;
            }
            .field-password .readonly a {
                font-size: 12px !important;
                color: #60a5fa !important;
                text-decoration: none !important;
                background: #1e3a5f !important;
                padding: 4px 12px !important;
                border-radius: 6px !important;
            }

            /* 4. DATE/TIME PICKER — space the "Today | Calendar" icons */
            .datetimeshortcuts {
                color: #475569 !important;
                font-size: 0.75rem !important;
                margin-left: 10px !important;
                white-space: nowrap !important;
            }
            .datetimeshortcuts a {
                color: #ff6b00 !important;
                text-transform: uppercase !important;
                font-weight: bold !important;
                font-size: 0.7rem !important;
            }

            /* 5. BUTTONS: Primary = Orange, Secondary = Outline */
            .submit-row {
                background: #0f1c2e !important;
                padding: 20px 30px !important;
                border-radius: 12px !important;
                display: flex !important;
                justify-content: flex-end !important;
                align-items: center !important;
                gap: 12px !important;
                border: 1px solid #1e293b !important;
            }
            .submit-row input[type="submit"] {
                border-radius: 50px !important;
                padding: 10px 28px !important;
                font-weight: 700 !important;
                border: none !important;
                font-size: 0.82rem !important;
                text-transform: uppercase !important;
                letter-spacing: 0.5px !important;
                cursor: pointer !important;
            }
            .submit-row input[name="_save"] {
                background: #ff6b00 !important;
                color: #fff !important;
                box-shadow: 0 4px 15px rgba(255, 107, 0, 0.35) !important;
            }
            .submit-row input[name="_addanother"],
            .submit-row input[name="_continue"] {
                background: transparent !important;
                border: 1px solid #334155 !important;
                color: #94a3b8 !important;
            }
            .deletelink, a.deletelink {
                background: rgba(239, 68, 68, 0.1) !important;
                color: #ef4444 !important;
                border: 1px solid #ef4444 !important;
                border-radius: 50px !important;
                padding: 10px 25px !important;
                font-size: 0.82rem !important;
                font-weight: 600 !important;
                text-decoration: none !important;
                text-transform: uppercase !important;
                transition: all 0.3s ease !important;
            }
            .deletelink:hover, a.deletelink:hover {
                background: #ef4444 !important;
                color: #fff !important;
                box-shadow: 0 0 15px rgba(239, 68, 68, 0.4) !important;
            }
        </style>
        """
        context['extra_css'] = mark_safe(anti_gravity_css)
        return super().render_change_form(request, context, *args, **kwargs)


# Safely unregister from default admin.site if present
try:
    admin.site.unregister(User)
except admin.sites.NotRegistered:
    pass

# Register Django's User model with the custom admin site
admin_site.register(User, CustomUserAdmin)


# ── Medical Records Admin ─────────────────────────────────────────────────────
@admin.register(MedicalRecord, site=admin_site)
class MedicalRecordAdmin(admin.ModelAdmin):
    list_display  = ('patient', 'report_name', 'uploaded_at', 'view_pdf_link')
    list_filter   = ('uploaded_at',)
    search_fields = ('patient__name', 'report_name')
    readonly_fields = ('uploaded_at', 'view_pdf_link')
    ordering      = ('-uploaded_at',)

    @admin.display(description='View PDF')
    def view_pdf_link(self, obj):
        from django.utils.html import format_html
        if obj.pdf_file:
            return format_html(
                '<a href="{}" target="_blank" '
                'style="color:#3b82f6;font-weight:700;">📄 Open PDF</a>',
                obj.pdf_file.url
            )
        return '—'
