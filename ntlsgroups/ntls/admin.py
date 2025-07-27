from django.contrib import admin
from django.core.mail import send_mail
from django.utils import timezone
from django import forms
from .models import Consumer, Business, Testimonial, Feedback, EmailConfig

class EmailConfigAdminForm(forms.ModelForm):
    class Meta:
        model = EmailConfig
        fields = '__all__'

    def clean(self):
        cleaned_data = super().clean()
        backend = cleaned_data.get('backend')
        if backend == 'django.core.mail.backends.smtp.EmailBackend':
            if not cleaned_data.get('email_id') or not cleaned_data.get('password'):
                raise forms.ValidationError('Email ID and password are required for SMTP backend.')
        return cleaned_data

@admin.register(EmailConfig)
class EmailConfigAdmin(admin.ModelAdmin):
    form = EmailConfigAdminForm
    list_display = ('email_id', 'purpose', 'is_active', 'host', 'port', 'updated_at')
    list_filter = ('purpose', 'is_active')
    search_fields = ('email_id',)
    actions = ['test_email']

    def test_email(self, request, queryset):
        for config in queryset:
            if config.is_active:
                try:
                    send_mail(
                        subject='Test Email from NTLS Group',
                        message=f'This is a test email sent using {config.email_id}.',
                        from_email=config.email_id,
                        recipient_list=[config.email_id],
                        fail_silently=False,
                        auth_user=config.email_id,
                        auth_password=config.password,
                    )
                    self.message_user(request, f'Test email sent successfully using {config.email_id}.')
                except Exception as e:
                    self.message_user(request, f'Failed to send test email using {config.email_id}: {str(e)}', level='error')
    test_email.short_description = 'Send test email'

@admin.register(Consumer)
class ConsumerAdmin(admin.ModelAdmin):
    list_display = ('name', 'contact', 'services', 'budget', 'created_at')
    search_fields = ('name', 'contact')

@admin.register(Business)
class BusinessAdmin(admin.ModelAdmin):
    list_display = ('name', 'contact', 'category', 'status', 'approved_date', 'suspended_date')
    list_filter = ('status', 'category')
    search_fields = ('name', 'contact')
    actions = ['approve_business', 'suspend_business', 'reject_business']

    def get_email_config(self, purpose):
        return EmailConfig.objects.filter(purpose=purpose, is_active=True).first() or EmailConfig.objects.filter(purpose='general', is_active=True).first()

    def approve_business(self, request, queryset):
        for business in queryset:
            if business.status != 'approved':
                business.status = 'approved'
                business.approved_date = timezone.now()
                business.suspended_date = None
                business.save()
                email_config = self.get_email_config('status_update')
                if email_config:
                    send_mail(
                        subject='Business Application Approved',
                        message=f'Dear {business.name},\n\nCongratulations! Your application to become a partner with NTLS Group has been approved.\n\nYou can now be matched with consumers seeking your services.\n\nBest regards,\nNTLS Group',
                        from_email=email_config.email_id,
                        recipient_list=[business.contact],
                        fail_silently=False,
                        auth_user=email_config.email_id,
                        auth_password=email_config.password,
                    )
        self.message_user(request, f'{queryset.count()} business(es) approved and notified.')
    approve_business.short_description = 'Approve selected businesses'

    def suspend_business(self, request, queryset):
        for business in queryset:
            if business.status != 'suspended':
                business.status = 'suspended'
                business.suspended_date = timezone.now()
                business.save()
                email_config = self.get_email_config('status_update')
                if email_config:
                    send_mail(
                        subject='Business Application Suspended',
                        message=f'Dear {business.name},\n\nYour partnership with NTLS Group has been suspended.\n\nPlease contact us for further details.\n\nBest regards,\nNTLS Group',
                        from_email=email_config.email_id,
                        recipient_list=[business.contact],
                        fail_silently=False,
                        auth_user=email_config.email_id,
                        auth_password=email_config.password,
                    )
        self.message_user(request, f'{queryset.count()} business(es) suspended and notified.')
    suspend_business.short_description = 'Suspend selected businesses'

    def reject_business(self, request, queryset):
        for business in queryset:
            if business.status != 'rejected':
                business.status = 'rejected'
                business.approved_date = None
                business.suspended_date = None
                business.save()
                email_config = self.get_email_config('status_update')
                if email_config:
                    send_mail(
                        subject='Business Application Rejected',
                        message=f'Dear {business.name},\n\nWe regret to inform you that your application to become a partner with NTLS Group has been rejected.\n\nPlease contact us for feedback.\n\nBest regards,\nNTLS Group',
                        from_email=email_config.email_id,
                        recipient_list=[business.contact],
                        fail_silently=False,
                        auth_user=email_config.email_id,
                        auth_password=email_config.password,
                    )
        self.message_user(request, f'{queryset.count()} business(es) rejected and notified.')
    reject_business.short_description = 'Reject selected businesses'

@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'message')
    search_fields = ('name', 'category')

@admin.register(Feedback)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'message', 'created_at')
    search_fields = ('name', 'email')