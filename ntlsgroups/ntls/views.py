from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import send_mail, get_connection
from django.utils import timezone
import logging
import smtplib
from .forms import ConsumerForm, BusinessForm, FeedbackForm
from .models import Consumer, Business, Testimonial, Feedback, EmailConfig, Blog, SocialPlatform, Service, PaymentLink, ContactInfo
from ntlsgroups.settings import get_email_config

# Set up logging
logger = logging.getLogger(__name__)

@csrf_exempt
def home(request):
    testimonials = Testimonial.objects.using('server').all()
    categories = Business.objects.using('server').filter(status='approved').values_list('category', flat=True).distinct()
    selected_category = request.GET.get('category', '')
    if selected_category:
        partners = Business.objects.using('server').filter(status='approved', category=selected_category)
    else:
        partners = Business.objects.using('server').filter(status='approved')
    partner_count = partners.count()
    blogs = Blog.objects.using('server').all().order_by('-created_at').prefetch_related('images')
    social_platforms = SocialPlatform.objects.using('server').filter(is_active=True)
    services = Service.objects.using('server').filter(is_active=True)
    payment_link = None
    contact_info = ContactInfo.objects.using('server').filter(is_active=True).first()

    try:
        payment_link = PaymentLink.objects.using('server').filter(is_active=True).first()
        if not payment_link:
            logger.info("No active payment link found in the database.")
    except Exception as e:
        logger.error(f"Failed to query PaymentLink table: {str(e)}. Continuing without payment link.")
        payment_link = None

    if request.method == 'POST':
        try:
            if 'consumer_form' in request.POST:
                logger.info(f"Consumer form POST data: {request.POST}")
                form = ConsumerForm(request.POST)
                if form.is_valid():
                    consumer = form.save(commit=False)
                    logger.debug(f"Consumer instance before save: {consumer.__dict__}")
                    consumer.save()  # Router handles dual writes
                    logger.info(f"Consumer saved: {consumer.name}, {consumer.contact}")
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
                                subject='Confirmation of Submission – Thank You',
                                message=f'Dear {consumer.name},\n\nWe have received your request/submission and would like to thank you for choosing NTLS GROUPS.\nYour submission is currently under processing. Our team will connect with you shortly to take the next steps or to provide further assistance.\n\nIf you need support or have any concerns, please write to:\nSujeeth Vishnu\nChief Business Development Executive\nsujeeth.cbde@ntlsgroups.org\n\nThis email is intended only for the recipient and should not be shared or replied to directly. All rights reserved. NTLS CONSULTANCY OPC PRIVATE LIMITED holds all legal rights over the content and communication.\n\nBest Regards, \nNTLS Groups',
                                from_email=email_config['EMAIL_HOST_USER'],
                                recipient_list=[consumer.contact],
                                fail_silently=False,
                                connection=connection
                            )
                            logger.info(f"Consumer email sent to {consumer.contact} from {email_config['EMAIL_HOST_USER']}")
                            return JsonResponse({'success': True, 'message': 'Form submitted successfully!'})
                        except smtplib.SMTPException as e:
                            logger.error(f"Email failed for {consumer.contact}: {str(e)}")
                            return JsonResponse({'success': False, 'message': 'Form submitted, but email failed. Please contact support.'})
                        except Exception as e:
                            logger.error(f"Unexpected email error for {consumer.contact}: {str(e)}")
                            return JsonResponse({'success': False, 'message': 'Form submitted, but an email error occurred. Please contact support.'})
                    else:
                        logger.error("No valid email configuration found")
                        return JsonResponse({'success': False, 'message': 'Form submitted, but no email configuration found. Please contact support.'})
                else:
                    logger.error(f"Consumer form errors: {form.errors}")
                    return JsonResponse({'success': False, 'message': 'Form submission failed.', 'errors': form.errors})

            elif 'business_form' in request.POST:
                logger.info(f"Business form POST data: {request.POST}, FILES: {request.FILES}")
                form = BusinessForm(request.POST, request.FILES)
                if form.is_valid():
                    business = form.save(commit=False)
                    full_contact = form.cleaned_data.get('full_contact')
                    if full_contact:
                        business.contact_number = full_contact
                        logger.debug(f"Updated business.contact_number with full_contact: {full_contact}")
                    else:
                        logger.warning("No full_contact found in cleaned_data")
                    logger.debug(f"Business instance before save: {business.__dict__}")
                    business.save()  # Router handles dual writes
                    logger.info(f"Business saved: {business.name}, {business.contact_number}")
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
                                subject='Submission Received – Under Review',
                                message=f'Dear {business.name},\n\nThis is to acknowledge that your application to partner with NTLS GROUPS has been received successfully.\nOur team is currently reviewing the information submitted. You will receive a follow-up email regarding the status of your application within 3–5 working days.\n\nIf you need to update any information or have questions during this review process, please contact:\nSujeeth Vishnu\nChief Business Development Executive\nsujeeth.cbde@ntlsgroups.org\n\nThis email is intended only for the recipient and should not be shared or replied to directly. All rights reserved. NTLS CONSULTANCY OPC PRIVATE LIMITED holds all legal rights over the content and communication.\n\nBest Regards, \nNTLS Groups',
                                from_email=email_config['EMAIL_HOST_USER'],
                                recipient_list=[business.contact],
                                fail_silently=False,
                                connection=connection
                            )
                            logger.info(f"Business email sent to {business.contact} from {email_config['EMAIL_HOST_USER']}")
                            return JsonResponse({'success': True, 'message': 'Application submitted successfully!'})
                        except smtplib.SMTPException as e:
                            logger.error(f"Email failed for {business.contact}: {str(e)}")
                            return JsonResponse({'success': False, 'message': 'Application submitted, but email failed. Please contact support.'})
                        except Exception as e:
                            logger.error(f"Unexpected email error for {business.contact}: {str(e)}")
                            return JsonResponse({'success': False, 'message': 'Application submitted, but an email error occurred. Please contact support.'})
                    else:
                        logger.error("No valid email configuration found")
                        return JsonResponse({'success': False, 'message': 'Application submitted, but no email configuration found. Please contact support.'})
                else:
                    logger.error(f"Business form errors: {form.errors}")
                    return JsonResponse({'success': False, 'message': 'Application submission failed.', 'errors': {k: [{'message': v[0]}] for k, v in form.errors.items()}})

            elif 'feedback_form' in request.POST:
                logger.info(f"Feedback form POST data: {request.POST}")
                form = FeedbackForm(request.POST)
                if form.is_valid():
                    feedback = form.save(commit=False)
                    feedback.save()  # Router handles dual writes
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
                                subject='Thank You for Your Feedback',
                                message=f'Dear {feedback.name},\n\nThank you for taking the time to share your feedback with NTLS GROUPS. We truly value your input and will use it to improve our services and offerings.\nIf your feedback requires a response, one of our representatives will be in touch with you shortly.\n\nFor assistance or complaints, please reach out to:\nSujeeth Vishnu\nChief Business Development Executive\nsujeeth.cbde@ntlsgroups.org\n\nThis email is intended only for the recipient and should not be shared or replied to directly. All rights reserved. NTLS CONSULTANCY OPC PRIVATE LIMITED holds all legal rights over the content and communication.\n\nBest Regards, \nNTLS Groups',
                                from_email=email_config['EMAIL_HOST_USER'],
                                recipient_list=[feedback.email],
                                fail_silently=False,
                                connection=connection
                            )
                            logger.info(f"Feedback email sent to {feedback.email} from {email_config['EMAIL_HOST_USER']}")
                            return JsonResponse({'success': True, 'message': 'Feedback submitted successfully!'})
                        except smtplib.SMTPException as e:
                            logger.error(f"Email failed for {feedback.email}: {str(e)}")
                            return JsonResponse({'success': False, 'message': 'Feedback submitted, but email failed. Please contact support.'})
                        except Exception as e:
                            logger.error(f"Unexpected email error for {feedback.email}: {str(e)}")
                            return JsonResponse({'success': False, 'message': 'Feedback submitted, but an email error occurred. Please contact support.'})
                    else:
                        logger.error("No valid email configuration found")
                        return JsonResponse({'success': False, 'message': 'Feedback submitted, but no email configuration found. Please contact support.'})
                else:
                    logger.error(f"Feedback form errors: {form.errors}")
                    return JsonResponse({'success': False, 'message': 'Feedback submission failed.', 'errors': form.errors})
        except Exception as e:
            logger.error(f"Unexpected error in POST request: {str(e)}", exc_info=True)
            return JsonResponse({'success': False, 'message': 'An unexpected server error occurred. Please try again or contact support.'})

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
        'payment_link': payment_link,
        'contact_info': contact_info,
    })

def privacy(request):
    payment_link = None
    try:
        payment_link = PaymentLink.objects.using('server').filter(is_active=True).first()
        if not payment_link:
            logger.info("No active payment link found in the database.")
    except Exception as e:
        logger.error(f"Failed to query PaymentLink table: {str(e)}. Continuing without payment link.")
        payment_link = None
    return render(request, 'ntls/privacy.html', {'payment_link': payment_link})

def terms(request):
    payment_link = None
    try:
        payment_link = PaymentLink.objects.using('server').filter(is_active=True).first()
        if not payment_link:
            logger.info("No active payment link found in the database.")
    except Exception as e:
        logger.error(f"Failed to query PaymentLink table: {str(e)}. Continuing without payment link.")
        payment_link = None
    return render(request, 'ntls/terms.html', {'payment_link': payment_link})