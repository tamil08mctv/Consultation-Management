from django.shortcuts import render
from django.http import JsonResponse
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from .forms import ConsumerForm, BusinessForm, FeedbackForm
from .models import Partner, Testimonial

def home(request):
    category = request.GET.get('category', '')
    partners = Partner.objects.filter(category__icontains=category) if category else Partner.objects.all()
    categories = Partner.objects.values_list('category', flat=True).distinct()
    testimonials = Testimonial.objects.all()[:3]
    consumer_form = ConsumerForm()
    business_form = BusinessForm()
    feedback_form = FeedbackForm()

    if request.method == 'POST':
        if 'consumer_form' in request.POST:
            consumer_form = ConsumerForm(request.POST)
            if consumer_form.is_valid():
                consumer_form.save()
                messages.success(request, 'Your request has been submitted successfully!')
                send_mail(
                    'Thank You for Your Submission',
                    f'Dear {consumer_form.cleaned_data["name"]},\n\nWe have received your request. Our team will contact you soon.\n\nBest regards,\nNTLS Group',
                    settings.DEFAULT_FROM_EMAIL,
                    [consumer_form.cleaned_data['contact']],
                    fail_silently=True,
                )
                return JsonResponse({'success': True, 'message': 'Your request has been submitted successfully!'})
            else:
                errors = {field: error[0] for field, error in consumer_form.errors.items()}
                return JsonResponse({'success': False, 'message': 'Please correct the errors in the Consumer form.', 'errors': errors})
        elif 'business_form' in request.POST:
            business_form = BusinessForm(request.POST, request.FILES)
            if business_form.is_valid():
                business_form.save()
                messages.success(request, 'Your application has been submitted successfully!')
                send_mail(
                    'Business Application Received',
                    f'Dear {business_form.cleaned_data["name"]},\n\nThank you for applying. We will review your application soon.\n\nBest regards,\nNTLS Group',
                    settings.DEFAULT_FROM_EMAIL,
                    [business_form.cleaned_data['contact']],
                    fail_silently=True,
                )
                return JsonResponse({'success': True, 'message': 'Your application has been submitted successfully!'})
            else:
                errors = {field: error[0] for field, error in business_form.errors.items()}
                return JsonResponse({'success': False, 'message': 'Please correct the errors in the Business form.', 'errors': errors})
        elif 'feedback_form' in request.POST:
            feedback_form = FeedbackForm(request.POST)
            if feedback_form.is_valid():
                feedback_form.save()
                messages.success(request, 'Thank you for your feedback!')
                send_mail(
                    'Thank You for Your Feedback',
                    f'Dear {feedback_form.cleaned_data["name"]},\n\nThank you for your feedback. We value your input!\n\nBest regards,\nNTLS Group',
                    settings.DEFAULT_FROM_EMAIL,
                    [feedback_form.cleaned_data['email']],
                    fail_silently=True,
                )
                return JsonResponse({'success': True, 'message': 'Thank you for your feedback!'})
            else:
                errors = {field: error[0] for field, error in feedback_form.errors.items()}
                return JsonResponse({'success': False, 'message': 'Please correct the errors in the Feedback form.', 'errors': errors})

    return render(request, 'ntls/home.html', {
        'partners': partners,
        'categories': categories,
        'testimonials': testimonials,
        'consumer_form': consumer_form,
        'business_form': business_form,
        'feedback_form': feedback_form,
        'partner_count': partners.count(),
    })