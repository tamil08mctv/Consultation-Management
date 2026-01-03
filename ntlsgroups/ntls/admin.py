from django.contrib import admin
from django.core.mail import send_mail, get_connection
from django.utils import timezone
from django import forms
from .models import Consumer, Business, Testimonial, Feedback, EmailConfig, Blog, BlogImage, SocialPlatform, Service, ContactInfo, PaymentLink
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
        if config and config['EMAIL_HOST_PASSWORD']:
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

    def save_model(self, request, obj, form, change):
        # Get the original object from the database to compare statuses
        original = Business.objects.get(pk=obj.pk) if change else None
        original_status = original.status if original else None

        # Save the object to the default (server) database
        super().save_model(request, obj, form, change)

        # Check if the status has changed and send email accordingly
        if change and original_status != obj.status:
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
                    subject = ''
                    message = ''
                    if obj.status == 'approved':
                        subject = 'Welcome to NTLS GROUPS – Partnership Approved'
                        message = f'Dear {obj.name},\n\nWe are pleased to inform you that your application to become a partner with NTLS GROUPS has been approved.\nYour submitted details and credentials have been reviewed and accepted. All the information provided will be retained and treated confidentially until the termination of the partnership, as per our privacy policy.\nYou are now officially part of our partner network, and we look forward to building a valuable and mutually beneficial relationship.\n\nIf you have any queries, complaints, or require future assistance, please contact:\nSujeeth Vishnu\nChief Business Development Executive\nsujeeth.cbde@ntlsgroups.org\n\nThis email is intended only for the recipient and should not be shared or replied to directly. All rights reserved. NTLS CONSULTANCY OPC PRIVATE LIMITED holds all legal rights over the content and communication.\n\nBest Regards, \nNTLS Groups'
                    elif obj.status == 'suspended':
                        subject = 'Account Suspended – Action Required'
                        message = f'Dear {obj.name},\n\nWe would like to inform you that your business partnership account with NTLS GROUPS has been temporarily suspended due to the following reason(s):\n• Incomplete compliance with required documentation\n• Misuse of partnership privileges\n• Breach of terms and conditions\nPlease reach out to our support team to resolve this matter. Failure to address the issue within 7 working days may lead to permanent termination.\n\nIf you need clarification or guidance, please get in touch with:\nSujeeth Vishnu\nChief Business Development Executive\nsujeeth.cbde@ntlsgroups.org\n\nThis email is intended only for the recipient and should not be shared or replied to directly. All rights reserved. NTLS CONSULTANCY OPC PRIVATE LIMITED holds all legal rights over the content and communication.\n\nBest Regards, \nNTLS Groups'
                    elif obj.status == 'rejected':
                        subject = 'Application Status – Not Approved'
                        message = f'Dear {obj.name},\n\nThank you for your interest in partnering with NTLS GROUPS.\nAfter careful review of your application, we regret to inform you that we are unable to approve your request at this time due to one or more of the following reasons:\n• Business listing name mismatch\n• Incomplete or unverifiable communication address\n• Missing or unclear documentation\n• Failure to meet our eligibility criteria\nYou are welcome to reapply after resolving the above issues. We appreciate your time and understanding.\n\nIf you believe this is a mistake or need further support, please feel free to contact:\nSujeeth Vishnu\nChief Business Development Executive\nsujeeth.cbde@ntlsgroups.org\n\nThis email is intended only for the recipient and should not be shared or replied to directly. All rights reserved. NTLS CONSULTANCY OPC PRIVATE LIMITED holds all legal rights over the content and communication.\n\nBest Regards, \nNTLS Groups'
                    elif obj.status == 'pending':
                        subject = 'Submission Received – Under Review'
                        message = f'Dear {obj.name},\n\nThis is to acknowledge that your application to partner with NTLS GROUPS has been received successfully.\nOur team is currently reviewing the information submitted. You will receive a follow-up email regarding the status of your application within 3–5 working days.\n\nIf you need to update any information or have questions during this review process, please contact:\nSujeeth Vishnu\nChief Business Development Executive\nsujeeth.cbde@ntlsgroups.org\n\nThis email is intended only for the recipient and should not be shared or replied to directly. All rights reserved. NTLS CONSULTANCY OPC PRIVATE LIMITED holds all legal rights over the content and communication.\n\nBest Regards, \nNTLS Groups'

                    if subject and message:
                        send_mail(
                            subject=subject,
                            message=message,
                            from_email=email_config['EMAIL_HOST_USER'],
                            recipient_list=[obj.contact],
                            fail_silently=False,
                            connection=connection
                        )
                        logger.info(f"Status change email sent to {obj.contact} from {email_config['EMAIL_HOST_USER']} for status {obj.status}")
                        self.message_user(request, f'Status change email sent to {obj.contact} for new status {obj.status}.')
                    else:
                        logger.warning(f"No email template defined for status {obj.status}")
                        self.message_user(request, f'No email template defined for status {obj.status}, email not sent.', level='warning')
                except smtplib.SMTPAuthenticationError as e:
                    logger.error(f"SMTP authentication failed for status change email to {obj.contact}: {str(e)}")
                    self.message_user(request, f'Failed to send status change email to {obj.contact}: Authentication failed - {str(e)}. Check email configuration.', level='error')
                except smtplib.SMTPConnectError as e:
                    logger.error(f"SMTP connection error for status change email to {obj.contact}: {str(e)}")
                    self.message_user(request, f'Failed to send status change email to {obj.contact}: Connection error - {str(e)}. Check email configuration.', level='error')
                except smtplib.SMTPRecipientsRefused as e:
                    logger.error(f"Recipient refused for status change email to {obj.contact}: {str(e)}")
                    self.message_user(request, f'Failed to send status change email to {obj.contact}: Recipient refused - {str(e)}.', level='error')
                except smtplib.SMTPException as e:
                    logger.error(f"SMTP error for status change email to {obj.contact}: {str(e)}")
                    self.message_user(request, f'Failed to send status change email to {obj.contact}: SMTP error - {str(e)}. Check email configuration.', level='error')
                except Exception as e:
                    logger.error(f"Unexpected error for status change email to {obj.contact}: {str(e)}")
                    self.message_user(request, f'Failed to send status change email to {obj.contact}: {str(e)}. Check email settings.', level='error')
            else:
                logger.error(f"No valid EmailConfig found for status change for {obj.name}")
                self.message_user(request, f'Status changed for {obj.name}, but no valid email configuration found.', level='error')

    def approve_business(self, request, queryset):
        success_count = 0
        for business in queryset:
            if business.status != 'approved':
                business.status = 'approved'
                business.approved_date = timezone.now()
                business.suspended_date = None
                business.save()
                success_count += 1
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
                            subject='Welcome to NTLS GROUPS – Partnership Approved',
                            message=f'Dear {business.name},\n\nWe are pleased to inform you that your application to become a partner with NTLS GROUPS has been approved.\nYour submitted details and credentials have been reviewed and accepted. All the information provided will be retained and treated confidentially until the termination of the partnership, as per our privacy policy.\nYou are now officially part of our partner network, and we look forward to building a valuable and mutually beneficial relationship.\n\nIf you have any queries, complaints, or require future assistance, please contact:\nSujeeth Vishnu\nChief Business Development Executive\nsujeeth.cbde@ntlsgroups.org\n\nThis email is intended only for the recipient and should not be shared or replied to directly. All rights reserved. NTLS CONSULTANCY OPC PRIVATE LIMITED holds all legal rights over the content and communication.\n\nBest Regards, \nNTLS Groups',
                            from_email=email_config['EMAIL_HOST_USER'],
                            recipient_list=[business.contact],
                            fail_silently=False,
                            connection=connection
                        )
                        logger.info(f"Approval email sent to {business.contact} from {email_config['EMAIL_HOST_USER']}")
                    except smtplib.SMTPException as e:
                        logger.error(f"Email failed for approval to {business.contact}: {str(e)}")
                        self.message_user(request, f'Approval email failed for {business.contact}: {str(e)}.', level='error')
                    except Exception as e:
                        logger.error(f"Unexpected email error for approval to {business.contact}: {str(e)}")
                        self.message_user(request, f'Unexpected email error for approval to {business.contact}: {str(e)}.', level='error')
        self.message_user(request, f'{success_count} business(es) approved successfully.')

    approve_business.short_description = 'Approve selected businesses'

    def suspend_business(self, request, queryset):
        success_count = 0
        for business in queryset:
            if business.status != 'suspended':
                business.status = 'suspended'
                business.suspended_date = timezone.now()
                business.approved_date = None
                business.save()
                success_count += 1
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
                            subject='Account Suspended – Action Required',
                            message=f'Dear {business.name},\n\nWe would like to inform you that your business partnership account with NTLS GROUPS has been temporarily suspended due to the following reason(s):\n• Incomplete compliance with required documentation\n• Misuse of partnership privileges\n• Breach of terms and conditions\nPlease reach out to our support team to resolve this matter. Failure to address the issue within 7 working days may lead to permanent termination.\n\nIf you need clarification or guidance, please get in touch with:\nSujeeth Vishnu\nChief Business Development Executive\nsujeeth.cbde@ntlsgroups.org\n\nThis email is intended only for the recipient and should not be shared or replied to directly. All rights reserved. NTLS CONSULTANCY OPC PRIVATE LIMITED holds all legal rights over the content and communication.\n\nBest Regards, \nNTLS Groups',
                            from_email=email_config['EMAIL_HOST_USER'],
                            recipient_list=[business.contact],
                            fail_silently=False,
                            connection=connection
                        )
                        logger.info(f"Suspension email sent to {business.contact} from {email_config['EMAIL_HOST_USER']}")
                    except smtplib.SMTPException as e:
                        logger.error(f"Email failed for suspension to {business.contact}: {str(e)}")
                        self.message_user(request, f'Suspension email failed for {business.contact}: {str(e)}.', level='error')
                    except Exception as e:
                        logger.error(f"Unexpected email error for suspension to {business.contact}: {str(e)}")
                        self.message_user(request, f'Unexpected email error for suspension to {business.contact}: {str(e)}.', level='error')
        self.message_user(request, f'{success_count} business(es) suspended successfully.')

    suspend_business.short_description = 'Suspend selected businesses'

    def reject_business(self, request, queryset):
        success_count = 0
        for business in queryset:
            if business.status != 'rejected':
                business.status = 'rejected'
                business.approved_date = None
                business.suspended_date = None
                business.save()
                success_count += 1
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
                            subject='Application Status – Not Approved',
                            message=f'Dear {business.name},\n\nThank you for your interest in partnering with NTLS GROUPS.\nAfter careful review of your application, we regret to inform you that we are unable to approve your request at this time due to one or more of the following reasons:\n• Business listing name mismatch\n• Incomplete or unverifiable communication address\n• Missing or unclear documentation\n• Failure to meet our eligibility criteria\nYou are welcome to reapply after resolving the above issues. We appreciate your time and understanding.\n\nIf you believe this is a mistake or need further support, please feel free to contact:\nSujeeth Vishnu\nChief Business Development Executive\nsujeeth.cbde@ntlsgroups.org\n\nThis email is intended only for the recipient and should not be shared or replied to directly. All rights reserved. NTLS CONSULTANCY OPC PRIVATE LIMITED holds all legal rights over the content and communication.\n\nBest Regards, \nNTLS Groups',
                            from_email=email_config['EMAIL_HOST_USER'],
                            recipient_list=[business.contact],
                            fail_silently=False,
                            connection=connection
                        )
                        logger.info(f"Rejection email sent to {business.contact} from {email_config['EMAIL_HOST_USER']}")
                    except smtplib.SMTPException as e:
                        logger.error(f"Email failed for rejection to {business.contact}: {str(e)}")
                        self.message_user(request, f'Rejection email failed for {business.contact}: {str(e)}.', level='error')
                    except Exception as e:
                        logger.error(f"Unexpected email error for rejection to {business.contact}: {str(e)}")
                        self.message_user(request, f'Unexpected email error for rejection to {business.contact}: {str(e)}.', level='error')
        self.message_user(request, f'{success_count} business(es) rejected successfully.')

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

@admin.register(ContactInfo)
class ContactInfoAdmin(admin.ModelAdmin):
    list_display = ('phone', 'email', 'is_active', 'updated_at')
    list_filter = ('is_active',)
    search_fields = ('phone', 'email')
    fields = ('phone', 'email', 'is_active')

@admin.register(PaymentLink)
class PaymentLinkAdmin(admin.ModelAdmin):
    list_display = ('link', 'is_active', 'created_at', 'updated_at')
    list_filter = ('is_active',)
    search_fields = ('link',)
    fields = ('link', 'is_active')

# ntls/admin.py
# === ADD THIS AT THE END OF YOUR admin.py ===

from django.contrib import admin
from django.utils.html import format_html
from django.http import HttpResponse
import csv
from .models import Project, ProjectField, ProjectFile, Submission


class ProjectFieldInline(admin.TabularInline):
    model = ProjectField
    extra = 3
    fields = ('order', 'label', 'field_type', 'options', 'required', 'unique_key')
    sortable_field_name = "order"


class ProjectFileInline(admin.TabularInline):
    model = ProjectFile
    extra = 2


class SubmissionInline(admin.TabularInline):
    model = Submission
    extra = 0
    readonly_fields = ('submitted_at', 'preview_submission')
    
    def preview_submission(self, obj):
        items = []
        for field in obj.project.fields.all():
            value = obj.data.get(field.label, '')
            if isinstance(value, str) and value.startswith('/media/'):
                items.append(f'<strong>{field.label}:</strong> <a href="{value}" target="_blank">Download File</a>')
            else:
                items.append(f'<strong>{field.label}:</strong> {value or "-"}')
        return format_html("<br>".join(items))
    preview_submission.short_description = "Submission Details"


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('college_name', 'project_name', 'is_active', 'created_at')
    inlines = [ProjectFileInline, ProjectFieldInline, SubmissionInline]

    actions = ['export_all_submissions_csv']

    def export_all_submissions_csv(self, request, queryset):
        if queryset.count() != 1:
            self.message_user(request, "Please select exactly ONE project to export.", level='error')
            return

        project = queryset.first()
        response = HttpResponse(content_type='text/csv; charset=utf-8')
        response['Content-Disposition'] = f'attachment; filename="{project.project_name}_All_Students.csv"'

        # Get field labels in correct order
        field_labels = [field.label for field in project.fields.all()]
        writer = csv.writer(response)
        writer.writerow(field_labels + ['Submitted At'])  # Header row

        for submission in project.submissions.all():
            row = [submission.data.get(label, '') for label in field_labels]
            row.append(submission.submitted_at.strftime('%Y-%m-%d %H:%M:%S'))
            writer.writerow(row)

        return response
    export_all_submissions_csv.short_description = "Export All Students (Perfect CSV)"


@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ('project', 'student_name', 'roll_number', 'submitted_at', 'view_files')
    list_filter = ('project__college_name', 'project__project_name', 'submitted_at')
    search_fields = ('data__Full Name', 'data__Roll Number', 'data__Name', 'data__Regno')
    date_hierarchy = 'submitted_at'

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('project')

    def student_name(self, obj):
        return obj.data.get('Full Name') or obj.data.get('Name') or '—'
    student_name.short_description = "Student Name"

    def roll_number(self, obj):
        return obj.data.get('Roll Number') or obj.data.get('Regno') or '—'
    roll_number.short_description = "Roll No"

    def view_files(self, obj):
        links = obj.get_file_links()
        if not links:
            return "No files"
        return format_html('<br>'.join([
            f'<a href="{url}" target="_blank">Download {label}</a>' for label, url in links
        ]))
    view_files.short_description = "Files"

    actions = ['export_selected_as_csv']

    def export_selected_as_csv(self, request, queryset):
        response = HttpResponse(content_type='text/csv; charset=utf-8')
        response['Content-Disposition'] = 'attachment; filename="Selected_Submissions.csv"'

        if not queryset.exists():
            return response

        project = queryset.first().project
        field_labels = [f.label for f in project.fields.all()]
        writer = csv.writer(response)
        writer.writerow(field_labels + ['Submitted At'])

        for sub in queryset:
            row = [sub.data.get(label, '') for label in field_labels]
            row.append(sub.submitted_at.strftime('%Y-%m-%d %H:%M:%S'))
            writer.writerow(row)

        return response
    export_selected_as_csv.short_description = "Export Selected (Perfect Columns)"