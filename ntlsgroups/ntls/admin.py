from django.contrib import admin
from django.core.mail import send_mail
from django.conf import settings
from .models import Consumer, Business, Partner, Testimonial, Feedback
from django.core.files import File
import os

@admin.register(Consumer)
class ConsumerAdmin(admin.ModelAdmin):
    list_display = ('name', 'contact', 'services', 'budget', 'submission_date')

@admin.register(Business)
class BusinessAdmin(admin.ModelAdmin):
    list_display = ('name', 'contact', 'category', 'status', 'submission_date')
    list_filter = ('status', 'category')
    actions = ['approve_business', 'reject_business']

    def approve_business(self, request, queryset):
        for business in queryset:
            if business.status == 'pending':
                business.status = 'approved'
                business.save()
                # Create Partner instance
                partner_data = {
                    'name': business.name,
                    'category': business.category,
                    'description': business.services,
                }
                if business.logo:
                    # Ensure logo file exists and is accessible
                    logo_path = business.logo.path
                    if os.path.exists(logo_path):
                        with open(logo_path, 'rb') as logo_file:
                            partner = Partner(**partner_data)
                            partner.logo.save(business.logo.name, File(logo_file), save=True)
                    else:
                        partner = Partner.objects.create(**partner_data)
                else:
                    partner = Partner.objects.create(**partner_data)
                send_mail(
                    'Application Approved',
                    f'Dear {business.name},\n\nCongratulations! Your application has been approved. You are now a partner with NTLS Group.\n\nBest regards,\nNTLS Group',
                    settings.DEFAULT_FROM_EMAIL,
                    [business.contact],
                    fail_silently=True,
                )
                self.message_user(request, f"{business.name} has been approved and added as a partner.")
    approve_business.short_description = "Approve selected businesses and add as partners"

    def reject_business(self, request, queryset):
        for business in queryset:
            if business.status == 'pending':
                business.status = 'rejected'
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

@admin.register(Partner)
class PartnerAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'description', 'logo')

@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'message')

@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'message', 'submission_date')