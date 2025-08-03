from django.contrib import admin
from django.core.mail import send_mail, get_connection
from django.utils import timezone
from django import forms
from .models import Consumer, Business, Testimonial, Feedback, EmailConfig, Blog, BlogImage, SocialPlatform, Service
import logging
import smtplib
import re
from ntlsgroups.settings import get_email_config

# Set up logging
logger = logging.getLogger(__name__)

class EmailConfigAdminForm(forms.ModelForm):
    class Meta:
        model = EmailConfig
        fields = '__all__'

    def clean(self):
        cleaned_data = super().clean()
        backend = cleaned_data.get('backend')
        if backend == 'django.core.mail.backends.smtp.EmailBackend':
            email_id = cleaned_data.get('email_id')
            password = cleaned_data.get('password')
            host = cleaned_data.get('host')
            port = cleaned_data.get('port')
            use_tls = cleaned_data.get('use_tls')

            if not email_id or not password:
                raise forms.ValidationError('Email ID and password are required for SMTP backend.')

            if 'gmail.com' in email_id.lower():
                if not re.match(r'^[a-z]{4}\s[a-z]{4}\s[a-z]{4}\s[a-z]{4}$', password):
                    logger.warning(f"Password for {email_id} does not match Gmail App Password format.")
                    self.add_error('password', 'Gmail requires a 16-character App Password (e.g., abcd efgh ijkl mnop). Ensure 2-Step Verification is enabled.')

            try:
                with smtplib.SMTP(host, port) as server:
                    if use_tls:
                        server.starttls()
                    server.login(email_id, password)
                    logger.info(f"SMTP validation successful for {email_id}")
            except smtplib.SMTPAuthenticationError as e:
                logger.error(f"SMTP authentication failed for {email_id}: {str(e)}")
                raise forms.ValidationError(f"SMTP authentication failed: {str(e)}. Check App Password and 2-Step Verification.")
            except smtplib.SMTPConnectError as e:
                logger.error(f"SMTP connection error for {email_id}: {str(e)}")
                raise forms.ValidationError(f"SMTP connection error: {str(e)}. Verify host and port.")
            except smtplib.SMTPException as e:
                logger.error(f"SMTP error for {email_id}: {str(e)}")
                raise forms.ValidationError(f"SMTP error: {str(e)}")
            except Exception as e:
                logger.error(f"Unexpected error validating SMTP for {email_id}: {str(e)}")
                raise forms.ValidationError(f"Unexpected error: {str(e)}")

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
                    connection = get_connection(
                        backend='django.core.mail.backends.smtp.EmailBackend',
                        host=config.host,
                        port=config.port,
                        username=config.email_id,
                        password=config.password,
                        use_tls=config.use_tls
                    )
                    send_mail(
                        subject='Test Email from NTLS Group',
                        message=f'This is a test email sent using {config.email_id}.',
                        from_email=config.email_id,
                        recipient_list=[config.email_id],
                        fail_silently=False,
                        connection=connection
                    )
                    logger.info(f"Test email sent successfully to {config.email_id}")
                    self.message_user(request, f'Test email sent successfully using {config.email_id}.')
                except smtplib.SMTPAuthenticationError as e:
                    logger.error(f"SMTP authentication failed for test email to {config.email_id}: {str(e)}")
                    self.message_user(request, f'Failed to send test email using {config.email_id}: Authentication failed - {str(e)}. Check App Password and 2-Step Verification.', level='error')
                except smtplib.SMTPConnectError as e:
                    logger.error(f"SMTP connection error for test email to {config.email_id}: {str(e)}")
                    self.message_user(request, f'Failed to send test email using {config.email_id}: Connection error - {str(e)}. Verify host and port.', level='error')
                except smtplib.SMTPException as e:
                    logger.error(f"SMTP error for test email to {config.email_id}: {str(e)}")
                    self.message_user(request, f'Failed to send test email using {config.email_id}: SMTP error - {str(e)}.', level='error')
                except Exception as e:
                    logger.error(f"Unexpected error for test email to {config.email_id}: {str(e)}")
                    self.message_user(request, f'Failed to send test email using {config.email_id}: {str(e)}.', level='error')
    test_email.short_description = 'Send test email'

class BusinessAdminForm(forms.ModelForm):
    class Meta:
        model = Business
        fields = '__all__'

    def clean(self):
        cleaned_data = super().clean()
        status = cleaned_data.get('status')
        approved_date = cleaned_data.get('approved_date')
        suspended_date = cleaned_data.get('suspended_date')

        if status == 'approved' and not approved_date:
            cleaned_data['approved_date'] = timezone.now()
            cleaned_data['suspended_date'] = None
        elif status == 'suspended' and not suspended_date:
            cleaned_data['suspended_date'] = timezone.now()
            cleaned_data['approved_date'] = None
        elif status in ['pending', 'rejected']:
            cleaned_data['approved_date'] = None
            cleaned_data['suspended_date'] = None

        return cleaned_data

@admin.register(Consumer)
class ConsumerAdmin(admin.ModelAdmin):
    list_display = ('name', 'contact', 'services', 'created_at')
    search_fields = ('name', 'contact')

@admin.register(Business)
class BusinessAdmin(admin.ModelAdmin):
    form = BusinessAdminForm
    list_display = ('name', 'contact', 'state', 'district', 'business_mode', 'category', 'contact_number', 'status', 'approved_date', 'suspended_date')
    list_filter = ('status', 'category', 'state', 'district', 'business_mode')
    search_fields = ('name', 'contact', 'contact_number')
    actions = ['approve_business', 'suspend_business', 'reject_business']

    def get_email_config(self):
        config = get_email_config()
        if config['EMAIL_HOST_PASSWORD']:
            logger.info(f"Using email config for {config['EMAIL_HOST_USER']}")
            try:
                with smtplib.SMTP(config['EMAIL_HOST'], config['EMAIL_PORT']) as server:
                    if config['EMAIL_USE_TLS']:
                        server.starttls()
                    server.login(config['EMAIL_HOST_USER'], config['EMAIL_HOST_PASSWORD'])
                    logger.info(f"SMTP validation successful for {config['EMAIL_HOST_USER']}")
                    return config
            except smtplib.SMTPAuthenticationError as e:
                logger.error(f"SMTP authentication failed for {config['EMAIL_HOST_USER']}: {str(e)}")
                return None
            except smtplib.SMTPConnectError as e:
                logger.error(f"SMTP connection error for {config['EMAIL_HOST_USER']}: {str(e)}")
                return None
            except smtplib.SMTPException as e:
                logger.error(f"SMTP error for {config['EMAIL_HOST_USER']}: {str(e)}")
                return None
            except Exception as e:
                logger.error(f"Unexpected error validating SMTP for {config['EMAIL_HOST_USER']}: {str(e)}")
                return None
        else:
            logger.error("No valid EmailConfig found or password missing")
            return None

    def approve_business(self, request, queryset):
        for business in queryset:
            if business.status != 'approved':
                business.status = 'approved'
                business.approved_date = timezone.now()
                business.suspended_date = None
                business.save(using='server')
                try:
                    business.save(using='default')
                except Exception as e:
                    logger.error(f"Failed to save to local database for approval: {str(e)}")
                    self.message_user(request, f'Business approved on server, but failed to save to local: {str(e)}.', level='error')
                email_config = self.get_email_config()
                if email_config:
                    try:
                        connection = get_connection(
                            backend='django.core.mail.backends.smtp.EmailBackend',
                            host=email_config['EMAIL_HOST'],
                            port=email_config['EMAIL_PORT'],
                            username=email_config['EMAIL_HOST_USER'],
                            password=email_config['EMAIL_HOST_PASSWORD'],
                            use_tls=email_config['EMAIL_USE_TLS']
                        )
                        send_mail(
                            subject='Business Application Approved',
                            message=f'Dear {business.name},\n\nCongratulations! Your application to become a partner with NTLS Group has been approved.\n\nYou can now be matched with customers seeking your services.\n\nBest regards,\nNTLS Group',
                            from_email=email_config['EMAIL_HOST_USER'],
                            recipient_list=[business.contact],
                            fail_silently=False,
                            connection=connection
                        )
                        logger.info(f"Approval email sent to {business.contact} from {email_config['EMAIL_HOST_USER']}")
                    except smtplib.SMTPAuthenticationError as e:
                        logger.error(f"SMTP authentication failed for approval email to {business.contact}: {str(e)}")
                        self.message_user(request, f'Business approved, but failed to send email to {business.contact}: Authentication failed - {str(e)}. Check email configuration.', level='error')
                    except smtplib.SMTPConnectError as e:
                        logger.error(f"SMTP connection error for approval email to {business.contact}: {str(e)}")
                        self.message_user(request, f'Business approved, but failed to send email to {business.contact}: Connection error - {str(e)}. Check email configuration.', level='error')
                    except smtplib.SMTPRecipientsRefused as e:
                        logger.error(f"Recipient refused for approval email to {business.contact}: {str(e)}")
                        self.message_user(request, f'Business approved, but failed to send email to {business.contact}: Recipient refused - {str(e)}.', level='error')
                    except smtplib.SMTPException as e:
                        logger.error(f"SMTP error for approval email to {business.contact}: {str(e)}")
                        self.message_user(request, f'Business approved, but failed to send email to {business.contact}: SMTP error - {str(e)}. Check email configuration.', level='error')
                    except Exception as e:
                        logger.error(f"Unexpected error for approval email to {business.contact}: {str(e)}")
                        self.message_user(request, f'Business approved, but failed to send email to {business.contact}: {str(e)}. Check email settings.', level='error')
                else:
                    logger.error("No valid EmailConfig found for business approval")
                    self.message_user(request, f'Business approved, but no valid email configuration found.', level='error')
        self.message_user(request, f'{queryset.count()} business(es) approved.')
    approve_business.short_description = 'Approve selected businesses'

    def suspend_business(self, request, queryset):
        for business in queryset:
            if business.status != 'suspended':
                business.status = 'suspended'
                business.suspended_date = timezone.now()
                business.approved_date = None
                business.save(using='server')
                try:
                    business.save(using='default')
                except Exception as e:
                    logger.error(f"Failed to save to local database for suspension: {str(e)}")
                    self.message_user(request, f'Business suspended on server, but failed to save to local: {str(e)}.', level='error')
                email_config = self.get_email_config()
                if email_config:
                    try:
                        connection = get_connection(
                            backend='django.core.mail.backends.smtp.EmailBackend',
                            host=email_config['EMAIL_HOST'],
                            port=email_config['EMAIL_PORT'],
                            username=email_config['EMAIL_HOST_USER'],
                            password=email_config['EMAIL_HOST_PASSWORD'],
                            use_tls=email_config['EMAIL_USE_TLS']
                        )
                        send_mail(
                            subject='Business Application Suspended',
                            message=f'Dear {business.name},\n\nYour partnership with NTLS Group has been suspended.\n\nPlease contact us for further details.\n\nBest regards,\nNTLS Group',
                            from_email=email_config['EMAIL_HOST_USER'],
                            recipient_list=[business.contact],
                            fail_silently=False,
                            connection=connection
                        )
                        logger.info(f"Suspension email sent to {business.contact} from {email_config['EMAIL_HOST_USER']}")
                    except smtplib.SMTPAuthenticationError as e:
                        logger.error(f"SMTP authentication failed for suspension email to {business.contact}: {str(e)}")
                        self.message_user(request, f'Business suspended, but failed to send email to {business.contact}: Authentication failed - {str(e)}. Check email configuration.', level='error')
                    except smtplib.SMTPConnectError as e:
                        logger.error(f"SMTP connection error for suspension email to {business.contact}: {str(e)}")
                        self.message_user(request, f'Business suspended, but failed to send email to {business.contact}: Connection error - {str(e)}. Check email configuration.', level='error')
                    except smtplib.SMTPRecipientsRefused as e:
                        logger.error(f"Recipient refused for suspension email to {business.contact}: {str(e)}")
                        self.message_user(request, f'Business suspended, but failed to send email to {business.contact}: Recipient refused - {str(e)}.', level='error')
                    except smtplib.SMTPException as e:
                        logger.error(f"SMTP error for suspension email to {business.contact}: {str(e)}")
                        self.message_user(request, f'Business suspended, but failed to send email to {business.contact}: SMTP error - {str(e)}. Check email configuration.', level='error')
                    except Exception as e:
                        logger.error(f"Unexpected error for suspension email to {business.contact}: {str(e)}")
                        self.message_user(request, f'Business suspended, but failed to send email to {business.contact}: {str(e)}. Check email settings.', level='error')
                else:
                    logger.error("No valid EmailConfig found for business suspension")
                    self.message_user(request, f'Business suspended, but no valid email configuration found.', level='error')
        self.message_user(request, f'{queryset.count()} business(es) suspended.')
    suspend_business.short_description = 'Suspend selected businesses'

    def reject_business(self, request, queryset):
        for business in queryset:
            if business.status != 'rejected':
                business.status = 'rejected'
                business.approved_date = None
                business.suspended_date = None
                business.save(using='server')
                try:
                    business.save(using='default')
                except Exception as e:
                    logger.error(f"Failed to save to local database for rejection: {str(e)}")
                    self.message_user(request, f'Business rejected on server, but failed to save to local: {str(e)}.', level='error')
                email_config = self.get_email_config()
                if email_config:
                    try:
                        connection = get_connection(
                            backend='django.core.mail.backends.smtp.EmailBackend',
                            host=email_config['EMAIL_HOST'],
                            port=email_config['EMAIL_PORT'],
                            username=email_config['EMAIL_HOST_USER'],
                            password=email_config['EMAIL_HOST_PASSWORD'],
                            use_tls=email_config['EMAIL_USE_TLS']
                        )
                        send_mail(
                            subject='Business Application Rejected',
                            message=f'Dear {business.name},\n\nWe regret to inform you that your application to become a partner with NTLS Group has been rejected.\n\nPlease contact us for feedback.\n\nBest regards,\nNTLS Group',
                            from_email=email_config['EMAIL_HOST_USER'],
                            recipient_list=[business.contact],
                            fail_silently=False,
                            connection=connection
                        )
                        logger.info(f"Rejection email sent to {business.contact} from {email_config['EMAIL_HOST_USER']}")
                    except smtplib.SMTPAuthenticationError as e:
                        logger.error(f"SMTP authentication failed for rejection email to {business.contact}: {str(e)}")
                        self.message_user(request, f'Business rejected, but failed to send email to {business.contact}: Authentication failed - {str(e)}. Check email configuration.', level='error')
                    except smtplib.SMTPConnectError as e:
                        logger.error(f"SMTP connection error for rejection email to {business.contact}: {str(e)}")
                        self.message_user(request, f'Business rejected, but failed to send email to {business.contact}: Connection error - {str(e)}. Check email configuration.', level='error')
                    except smtplib.SMTPRecipientsRefused as e:
                        logger.error(f"Recipient refused for rejection email to {business.contact}: {str(e)}")
                        self.message_user(request, f'Business rejected, but failed to send email to {business.contact}: Recipient refused - {str(e)}.', level='error')
                    except smtplib.SMTPException as e:
                        logger.error(f"SMTP error for rejection email to {business.contact}: {str(e)}")
                        self.message_user(request, f'Business rejected, but failed to send email to {business.contact}: SMTP error - {str(e)}. Check email configuration.', level='error')
                    except Exception as e:
                        logger.error(f"Unexpected error for rejection email to {business.contact}: {str(e)}")
                        self.message_user(request, f'Business rejected, but failed to send email to {business.contact}: {str(e)}. Check email settings.', level='error')
                else:
                    logger.error("No valid EmailConfig found for business rejection")
                    self.message_user(request, f'Business rejected, but no valid email configuration found.', level='error')
        self.message_user(request, f'{queryset.count()} business(es) rejected.')
    reject_business.short_description = 'Reject selected businesses'

@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'message')
    search_fields = ('name', 'category')

@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'message', 'created_at')
    search_fields = ('name', 'email')

class BlogImageInline(admin.TabularInline):
    model = BlogImage
    extra = 1
    fields = ('image', 'caption')

@admin.register(Blog)
class BlogAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at')
    search_fields = ('title', 'content')
    inlines = [BlogImageInline]

@admin.register(SocialPlatform)
class SocialPlatformAdmin(admin.ModelAdmin):
    list_display = ('name', 'link', 'is_active', 'created_at')
    list_filter = ('is_active', 'name')
    search_fields = ('name', 'link')

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'icon', 'icon_image', 'is_active', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('name', 'icon')
    fields = ('name', 'icon', 'icon_image', 'description', 'is_active')