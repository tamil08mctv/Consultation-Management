from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import send_mail, get_connection
from django.utils import timezone
import logging
import smtplib
from .forms import ConsumerForm, BusinessForm, FeedbackForm
from .models import Consumer, Business, Testimonial, Feedback, EmailConfig, Blog, SocialPlatform, Service
from ntlsgroups.settings import get_email_config

# Set up logging
logger = logging.getLogger(__name__)

@csrf_exempt
def home(request):
    testimonials = Testimonial.objects.all()
    categories = Business.objects.filter(status='approved').values_list('category', flat=True).distinct()
    selected_category = request.GET.get('category', '')
    if selected_category:
        partners = Business.objects.filter(status='approved', category=selected_category)
    else:
        partners = Business.objects.filter(status='approved')
    partner_count = partners.count()
    blogs = Blog.objects.all().order_by('-created_at').prefetch_related('images')
    social_platforms = SocialPlatform.objects.filter(is_active=True)
    services = Service.objects.filter(is_active=True)

    if request.method == 'POST':
        if 'consumer_form' in request.POST:
            logger.info(f"Consumer form POST data: {request.POST}")
            form = ConsumerForm(request.POST)
            if form.is_valid():
                consumer = form.save()
                email_config = get_email_config()
                if email_config and email_config['EMAIL_HOST_PASSWORD']:
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
                            subject='Consumer Form Submission Confirmation',
                            message=f'Dear {consumer.name},\n\nThank you for submitting your needs to NTLS Group.\n\nDetails:\n- Services: {consumer.services}\n\nWe will connect you with a suitable partner soon.\n\nBest regards,\nNTLS Group',
                            from_email=email_config['EMAIL_HOST_USER'],
                            recipient_list=[consumer.contact],
                            fail_silently=False,
                            connection=connection
                        )
                        logger.info(f"Consumer email sent to {consumer.contact} from {email_config['EMAIL_HOST_USER']}")
                        return JsonResponse({'success': True, 'message': 'Form submitted successfully!'})
                    except smtplib.SMTPAuthenticationError as e:
                        logger.error(f"SMTP authentication failed for consumer email to {consumer.contact}: {str(e)}")
                        return JsonResponse({'success': False, 'message': 'Form submitted, but email authentication failed. Please contact support.'})
                    except smtplib.SMTPConnectError as e:
                        logger.error(f"SMTP connection error for consumer email to {consumer.contact}: {str(e)}")
                        return JsonResponse({'success': False, 'message': 'Form submitted, but email connection failed. Please contact support.'})
                    except smtplib.SMTPRecipientsRefused as e:
                        logger.error(f"Recipient refused for consumer email to {consumer.contact}: {str(e)}")
                        return JsonResponse({'success': False, 'message': 'Form submitted, but email failed due to invalid recipient. Please contact support.'})
                    except smtplib.SMTPException as e:
                        logger.error(f"SMTP error for consumer email to {consumer.contact}: {str(e)}")
                        return JsonResponse({'success': False, 'message': 'Form submitted, but email failed. Please contact support.'})
                    except Exception as e:
                        logger.error(f"Unexpected error for consumer email to {consumer.contact}: {str(e)}")
                        return JsonResponse({'success': False, 'message': 'Form submitted, but an error occurred. Please contact support.'})
                else:
                    logger.error("No valid email configuration found")
                    return JsonResponse({'success': False, 'message': 'Form submitted, but no email configuration found. Please contact support.'})
            else:
                logger.error(f"Consumer form errors: {form.errors}")
                return JsonResponse({'success': False, 'message': 'Form submission failed.', 'errors': form.errors.as_json()})
        
        elif 'business_form' in request.POST:
            logger.info(f"Business form POST data: {request.POST}, FILES: {request.FILES}")
            form = BusinessForm(request.POST, request.FILES)
            if form.is_valid():
                business = form.save()
                email_config = get_email_config()
                if email_config and email_config['EMAIL_HOST_PASSWORD']:
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
                            subject='Business Application Received',
                            message=f'Dear {business.name},\n\nThank you for applying to become a partner with NTLS Group.\n\nDetails:\n- Category: {business.get_category_display()}\n- Location: {business.district}, {business.state}\n- Mode: {business.get_business_mode_display()}\n- Contact Number: {business.contact_number}\n- Applier Designation: {business.applier_designation}\n\nWe will review your application and notify you of the status.\n\nBest regards,\nNTLS Group',
                            from_email=email_config['EMAIL_HOST_USER'],
                            recipient_list=[business.contact],
                            fail_silently=False,
                            connection=connection
                        )
                        logger.info(f"Business email sent to {business.contact} from {email_config['EMAIL_HOST_USER']}")
                        return JsonResponse({'success': True, 'message': 'Application submitted successfully!'})
                    except smtplib.SMTPAuthenticationError as e:
                        logger.error(f"SMTP authentication failed for business email to {business.contact}: {str(e)}")
                        return JsonResponse({'success': False, 'message': 'Application submitted, but email authentication failed. Please contact support.'})
                    except smtplib.SMTPConnectError as e:
                        logger.error(f"SMTP connection error for business email to {business.contact}: {str(e)}")
                        return JsonResponse({'success': False, 'message': 'Application submitted, but email connection failed. Please contact support.'})
                    except smtplib.SMTPRecipientsRefused as e:
                        logger.error(f"Recipient refused for business email to {business.contact}: {str(e)}")
                        return JsonResponse({'success': False, 'message': 'Application submitted, but email failed due to invalid recipient. Please contact support.'})
                    except smtplib.SMTPException as e:
                        logger.error(f"SMTP error for business email to {business.contact}: {str(e)}")
                        return JsonResponse({'success': False, 'message': 'Application submitted, but email failed. Please contact support.'})
                    except Exception as e:
                        logger.error(f"Unexpected error for business email to {business.contact}: {str(e)}")
                        return JsonResponse({'success': False, 'message': 'Application submitted, but an error occurred. Please contact support.'})
                else:
                    logger.error("No valid email configuration found")
                    return JsonResponse({'success': False, 'message': 'Application submitted, but no email configuration found. Please contact support.'})
            else:
                logger.error(f"Business form errors: {form.errors}")
                return JsonResponse({'success': False, 'message': 'Application submission failed.', 'errors': form.errors.as_json()})
        
        elif 'feedback_form' in request.POST:
            logger.info(f"Feedback form POST data: {request.POST}")
            form = FeedbackForm(request.POST)
            if form.is_valid():
                feedback = form.save()
                email_config = get_email_config()
                if email_config and email_config['EMAIL_HOST_PASSWORD']:
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
                            subject='Feedback Submission Confirmation',
                            message=f'Dear {feedback.name},\n\nThank you for your feedback to NTLS Group.\n\nMessage:\n{feedback.message}\n\nWe value your input and will get back to you soon.\n\nBest regards,\nNTLS Group',
                            from_email=email_config['EMAIL_HOST_USER'],
                            recipient_list=[feedback.email],
                            fail_silently=False,
                            connection=connection
                        )
                        logger.info(f"Feedback email sent to {feedback.email} from {email_config['EMAIL_HOST_USER']}")
                        return JsonResponse({'success': True, 'message': 'Feedback submitted successfully!'})
                    except smtplib.SMTPAuthenticationError as e:
                        logger.error(f"SMTP authentication failed for feedback email to {feedback.email}: {str(e)}")
                        return JsonResponse({'success': False, 'message': 'Feedback submitted, but email authentication failed. Please contact support.'})
                    except smtplib.SMTPConnectError as e:
                        logger.error(f"SMTP connection error for feedback email to {feedback.email}: {str(e)}")
                        return JsonResponse({'success': False, 'message': 'Feedback submitted, but email connection failed. Please contact support.'})
                    except smtplib.SMTPRecipientsRefused as e:
                        logger.error(f"Recipient refused for feedback email to {feedback.email}: {str(e)}")
                        return JsonResponse({'success': False, 'message': 'Feedback submitted, but email failed due to invalid recipient. Please contact support.'})
                    except smtplib.SMTPException as e:
                        logger.error(f"SMTP error for feedback email to {feedback.email}: {str(e)}")
                        return JsonResponse({'success': False, 'message': 'Feedback submitted, but email failed. Please contact support.'})
                    except Exception as e:
                        logger.error(f"Unexpected error for feedback email to {feedback.email}: {str(e)}")
                        return JsonResponse({'success': False, 'message': 'Feedback submitted, but an error occurred. Please contact support.'})
                else:
                    logger.error("No valid email configuration found")
                    return JsonResponse({'success': False, 'message': 'Feedback submitted, but no email configuration found. Please contact support.'})
            else:
                logger.error(f"Feedback form errors: {form.errors}")
                return JsonResponse({'success': False, 'message': 'Feedback submission failed.', 'errors': form.errors.as_json()})

    consumer_form = ConsumerForm()
    business_form = BusinessForm()
    feedback_form = FeedbackForm()
    return render(request, 'ntls/home.html', {
        'testimonials': testimonials,
        'partners': partners,
        'partner_count': partner_count,
        'categories': categories,
        'consumer_form': consumer_form,
        'business_form': business_form,
        'feedback_form': feedback_form,
        'blogs': blogs,
        'social_platforms': social_platforms,
        'services': services,
    })