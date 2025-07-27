from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import send_mail
from django.utils import timezone
from .forms import ConsumerForm, BusinessForm, FeedbackForm
from .models import Consumer, Business, Testimonial, Feedback, EmailConfig

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
    
    def get_email_config(purpose):
        return EmailConfig.objects.filter(purpose=purpose, is_active=True).first() or EmailConfig.objects.filter(purpose='general', is_active=True).first()

    if request.method == 'POST':
        if 'consumer_form' in request.POST:
            form = ConsumerForm(request.POST)
            if form.is_valid():
                consumer = form.save()
                email_config = get_email_config('form_submission')
                if email_config:
                    send_mail(
                        subject='Consumer Form Submission Confirmation',
                        message=f'Dear {consumer.name},\n\nThank you for submitting your needs to NTLS Group.\n\nDetails:\n- Services: {consumer.services}\n- Budget: {consumer.budget}\n\nWe will connect you with a suitable partner soon.\n\nBest regards,\nNTLS Group',
                        from_email=email_config.email_id,
                        recipient_list=[consumer.contact],
                        fail_silently=False,
                        auth_user=email_config.email_id,
                        auth_password=email_config.password,
                    )
                return JsonResponse({'success': True, 'message': 'Form submitted successfully!'})
            else:
                return JsonResponse({'success': False, 'message': 'Form submission failed.', 'errors': form.errors})
        
        elif 'business_form' in request.POST:
            form = BusinessForm(request.POST, request.FILES)
            if form.is_valid():
                business = form.save()
                email_config = get_email_config('form_submission')
                if email_config:
                    send_mail(
                        subject='Business Application Received',
                        message=f'Dear {business.name},\n\nThank you for applying to become a partner with NTLS Group.\n\nDetails:\n- Services: {business.description}\n- Category: {business.category}\n\nWe will review your application and notify you of the status.\n\nBest regards,\nNTLS Group',
                        from_email=email_config.email_id,
                        recipient_list=[business.contact],
                        fail_silently=False,
                        auth_user=email_config.email_id,
                        auth_password=email_config.password,
                    )
                return JsonResponse({'success': True, 'message': 'Application submitted successfully!'})
            else:
                return JsonResponse({'success': False, 'message': 'Application submission failed.', 'errors': form.errors})
        
        elif 'feedback_form' in request.POST:
            form = FeedbackForm(request.POST)
            if form.is_valid():
                feedback = form.save()
                email_config = get_email_config('notifications')
                if email_config:
                    send_mail(
                        subject='Feedback Submission Confirmation',
                        message=f'Dear {feedback.name},\n\nThank you for your feedback to NTLS Group.\n\nMessage:\n{feedback.message}\n\nWe value your input and will get back to you soon.\n\nBest regards,\nNTLS Group',
                        from_email=email_config.email_id,
                        recipient_list=[feedback.email],
                        fail_silently=False,
                        auth_user=email_config.email_id,
                        auth_password=email_config.password,
                    )
                return JsonResponse({'success': True, 'message': 'Feedback submitted successfully!'})
            else:
                return JsonResponse({'success': False, 'message': 'Feedback submission failed.', 'errors': form.errors})

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
    })