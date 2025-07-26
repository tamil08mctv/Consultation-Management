from django.contrib import admin
from django.core.mail import send_mail
from django.conf import settings
from .models import Consumer, Business, Testimonial, Feedback
from django.utils import timezone

@admin.register(Consumer)
class ConsumerAdmin(admin.ModelAdmin):
    list_display = ('name', 'contact', 'services', 'budget', 'submission_date')

@admin.register(Business)
class BusinessAdmin(admin.ModelAdmin):
    list_display = ('name', 'contact', 'category', 'status', 'submission_date', 'approved_date', 'suspended_date')
    list_filter = ('status', 'category')
    actions = ['approve_business', 'reject_business', 'suspend_business']
    readonly_fields = ('approved_date', 'suspended_date')

    def approve_business(self, request, queryset):
        for business in queryset:
            if business.status == 'pending':
                business.status = 'approved'
                business.approved_date = timezone.now()
                business.suspended_date = None
                business.save()
                send_mail(
                    'Application Approved',
                    f'Dear {business.name},\n\nCongratulations! Your application has been approved. You are now a partner with NTLS Group.\n\nBest regards,\nNTLS Group',
                    settings.DEFAULT_FROM_EMAIL,
                    [business.contact],
                    fail_silently=True,
                )
                self.message_user(request, f"{business.name} has been approved.")
    approve_business.short_description = "Approve selected businesses"

    def reject_business(self, request, queryset):
        for business in queryset:
            if business.status == 'pending':
                business.status = 'rejected'
                business.approved_date = None
                business.suspended_date = None
                business.save()
                send_mail(
                    'Application Status Update',
                    f'Dear {business.name},\n\nWe are unable to approve your application at this time.\n\nBest regards,\nNTLS Group',
                    settings.DEFAULT_FROM_EMAIL,
                    [business.contact],
                    fail_silently=True,
                )
                self.message_user(request, f"{business.name} has been rejected.")
    reject_business.short_description = "Reject selected businesses"

    def suspend_business(self, request, queryset):
        for business in queryset:
            if business.status in ['pending', 'approved']:
                business.status = 'suspend'
                business.suspended_date = timezone.now()
                business.approved_date = None
                business.save()
                send_mail(
                    'Business Partnership Suspended',
                    f'Dear {business.name},\n\nYour partnership with NTLS Group has been suspended. Please contact us for further details.\n\nBest regards,\nNTLS Group',
                    settings.DEFAULT_FROM_EMAIL,
                    [business.contact],
                    fail_silently=True,
                )
                self.message_user(request, f"{business.name} has been suspended.")
    suspend_business.short_description = "Suspend selected businesses"

@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'message')

@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'message', 'submission_date')