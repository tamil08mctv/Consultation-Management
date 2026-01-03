from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import send_mail, get_connection
from django.utils import timezone
import logging
import smtplib
from .forms import ConsumerForm, BusinessForm, FeedbackForm
from .models import Consumer, Business, Testimonial, Feedback, EmailConfig, Blog, SocialPlatform, Service, PaymentLink, ContactInfo, Submission
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
    payment_link = None
    contact_info = ContactInfo.objects.filter(is_active=True).first()

    try:
        payment_link = PaymentLink.objects.filter(is_active=True).first()
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
                    consumer = form.save()
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
                    business.save()
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
        payment_link = PaymentLink.objects.filter(is_active=True).first()
        if not payment_link:
            logger.info("No active payment link found in the database.")
    except Exception as e:
        logger.error(f"Failed to query PaymentLink table: {str(e)}. Continuing without payment link.")
        payment_link = None
    return render(request, 'ntls/privacy.html', {'payment_link': payment_link})

def terms(request):
    payment_link = None
    try:
        payment_link = PaymentLink.objects.filter(is_active=True).first()
        if not payment_link:
            logger.info("No active payment link found in the database.")
    except Exception as e:
        logger.error(f"Failed to query PaymentLink table: {str(e)}. Continuing without payment link.")
        payment_link = None
    return render(request, 'ntls/terms.html', {'payment_link': payment_link})

def custom_404(request, exception=None):
    return render(request, 'ntls/404.html', status=404)

# # ntls/views.py
# from django.shortcuts import render, get_object_or_404, redirect
# from django.contrib import messages
# from django.utils import timezone
# from django.conf import settings
# import os
# import csv
# from .models import Project, Submission


# def projects_list(request):
#     projects = Project.objects.filter(is_active=True).order_by('-created_at')
#     return render(request, 'ntls/projects_list.html', {'projects': projects})


# def project_detail(request, pk):
    # project = get_object_or_404(Project, pk=pk, is_active=True)

    # if request.method == 'POST':
    #     missing = []
    #     for field in project.fields.all():
    #         if field.required and not request.POST.get(field.label) and not request.FILES.get(field.label):
    #             missing.append(field.label)
    #     if missing:
    #         messages.error(request, f"Please fill: {', '.join(missing)}")
    #         return redirect('project_detail', pk=pk)

    #     # Build data
    #     data = {}
    #     unique_combo = {}

    #     for field in project.fields.all():
    #         label = field.label
    #         if field.field_type == 'file' and label in request.FILES:
    #             file = request.FILES[label]
    #             folder = os.path.join(settings.MEDIA_ROOT, 'student_files', str(project.id))
    #             os.makedirs(folder, exist_ok=True)
    #             # Use roll number in filename if available
    #             roll = request.POST.get('Roll Number', 'unknown') or request.POST.get('Reg No', 'unknown')
    #             safe_roll = "".join(c for c in roll if c.isalnum() or c in '_-')
    #             filename = f"{safe_roll}_{file.name}"
    #             path = os.path.join(folder, filename)
    #             with open(path, 'wb+') as f:
    #                 for chunk in file.chunks():
    #                     f.write(chunk)
    #             data[label] = f"/media/student_files/{project.id}/{filename}"
    #         else:
    #             value = request.POST.get(label, '')
    #             data[label] = value

    #         # Collect values for unique_key fields
    #         if field.unique_key:
    #             unique_combo[label] = value

    #     # Block duplicate if same unique values exist
    #     if unique_combo:
    #         if Submission.objects.filter(project=project, data__contains=unique_combo).exists():
    #             messages.error(request, "You have already submitted with this data (duplicate not allowed)!")
    #             return redirect('project_detail', pk=pk)

    #     # Save submission
    #     Submission.objects.create(project=project, data=data)

    #     # Append to CSV
    #     csv_path = project.csv_path()
    #     os.makedirs(os.path.dirname(csv_path), exist_ok=True)
    #     file_exists = os.path.exists(csv_path)
    #     with open(csv_path, 'a', newline='', encoding='utf-8') as f:
    #         writer = csv.DictWriter(f, fieldnames=data.keys())
    #         if not file_exists:
    #             writer.writeheader()
    #         writer.writerow(data)

    #     messages.success(request, "Submitted Successfully!")
    #     return redirect('project_detail', pk=pk)

    # return render(request, 'ntls/project_detail.html', {'project': project})

# === ADD THIS AT THE END OF YOUR views.py ===

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.utils import timezone
from django.conf import settings
import os
import csv
from .models import Project, Submission


def projects_list(request):
    projects = Project.objects.filter(is_active=True).order_by('-created_at')
    return render(request, 'ntls/projects_list.html', {'projects': projects})


def project_detail(request, pk):
    project = get_object_or_404(Project, pk=pk, is_active=True)

    if request.method == 'POST':
        # Validate required fields
        missing = [f.label for f in project.fields.all() if f.required and not request.POST.get(f.label) and not request.FILES.get(f.label)]
        if missing:
            messages.error(request, f"Required fields missing: {', '.join(missing)}")
            return redirect('project_detail', pk=pk)

        data = {}
        unique_values = {}

        for field in project.fields.all():
            label = field.label
            if field.field_type == 'file' and label in request.FILES:
                file = request.FILES[label]
                folder = os.path.join(settings.MEDIA_ROOT, 'student_files', str(project.id))
                os.makedirs(folder, exist_ok=True)
                
                roll = request.POST.get('Roll Number') or request.POST.get('Regno') or "unknown"
                safe_roll = "".join(c for c in str(roll) if c.isalnum() or c in "_-")
                filename = f"{safe_roll}_{file.name}"
                path = os.path.join(folder, filename)
                
                with open(path, 'wb+') as f:
                    for chunk in file.chunks():
                        f.write(chunk)
                data[label] = f"/media/student_files/{project.id}/{filename}"
            else:
                value = request.POST.get(label, '')
                data[label] = value

            # Collect unique key values
            if field.unique_key:
                unique_values[label] = value

        # Prevent duplicate submission
        if unique_values:
            if Submission.objects.filter(
                project=project,
                data__contains=unique_values
            ).exists():
                messages.error(request, "You already submitted with these details!")
                return redirect('project_detail', pk=pk)

        # Save
        Submission.objects.create(project=project, data=data)

        # Append to CSV
        csv_path = project.csv_path()
        os.makedirs(os.path.dirname(csv_path), exist_ok=True)
        file_exists = os.path.exists(csv_path)
        with open(csv_path, 'a', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=data.keys())
            if not file_exists:
                writer.writeheader()
            writer.writerow(data)

        messages.success(request, "Submitted successfully!")
        return redirect('project_detail', pk=pk)

    return render(request, 'ntls/project_detail.html', {'project': project})