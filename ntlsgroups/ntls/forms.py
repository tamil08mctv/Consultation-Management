from django import forms
from .models import Consumer, Business, Feedback

class ConsumerForm(forms.ModelForm):
    class Meta:
        model = Consumer
        fields = ['name', 'contact', 'services', 'budget']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Your Name', 'class': 'form-control', 'required': 'required'}),
            'contact': forms.EmailInput(attrs={'placeholder': 'your.email@example.com', 'class': 'form-control', 'required': 'required'}),
            'services': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Describe your needs (e.g., catering for 100 guests)', 'class': 'form-control', 'required': 'required'}),
            'budget': forms.TextInput(attrs={'placeholder': 'e.g., ₹10,000', 'class': 'form-control', 'required': 'required'}),
        }

class BusinessForm(forms.ModelForm):
    class Meta:
        model = Business
        fields = ['name', 'contact', 'services', 'category', 'file_upload', 'logo']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Business Name', 'class': 'form-control', 'required': 'required'}),
            'contact': forms.EmailInput(attrs={'placeholder': 'business.email@example.com', 'class': 'form-control', 'required': 'required'}),
            'services': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Describe your services', 'class': 'form-control', 'required': 'required'}),
            'category': forms.Select(choices=[
                ('Food', 'Food'),
                ('Retail', 'Retail'),
                ('Services', 'Services'),
                ('Other', 'Other'),
            ], attrs={'class': 'form-select', 'required': 'required'}),
            'file_upload': forms.FileInput(attrs={'data-bs-toggle': 'tooltip', 'title': 'Upload PDF only', 'class': 'form-control', 'accept': '.pdf', 'required': 'required'}),
            'logo': forms.FileInput(attrs={'data-bs-toggle': 'tooltip', 'title': 'Upload JPG/PNG, max 5MB', 'class': 'form-control', 'accept': '.jpg,.jpeg,.png'}),
        }

class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ['name', 'email', 'message']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Your Name', 'class': 'form-control', 'required': 'required'}),
            'email': forms.EmailInput(attrs={'placeholder': 'your.email@example.com', 'class': 'form-control', 'required': 'required'}),
            'message': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Your feedback', 'class': 'form-control', 'required': 'required'}),
        }