from django import forms
from .models import Consumer, Business, Feedback

class ConsumerForm(forms.ModelForm):
    class Meta:
        model = Consumer
        fields = ['name', 'contact', 'services', 'budget']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Your Name', 'class': 'form-control form-control-sm'}),
            'contact': forms.EmailInput(attrs={'placeholder': 'your.email@example.com', 'class': 'form-control form-control-sm'}),
            'services': forms.Textarea(attrs={'placeholder': 'Describe your needs', 'rows': 3, 'class': 'form-control form-control-sm'}),
            'budget': forms.TextInput(attrs={'placeholder': 'e.g., ₹10,000', 'class': 'form-control form-control-sm'}),
        }

class BusinessForm(forms.ModelForm):
    class Meta:
        model = Business
        fields = ['name', 'contact', 'description', 'category', 'file_upload', 'logo']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Business Name', 'class': 'form-control form-control-sm'}),
            'contact': forms.EmailInput(attrs={'placeholder': 'business.email@example.com', 'class': 'form-control form-control-sm'}),
            'description': forms.Textarea(attrs={'placeholder': 'Describe your services', 'rows': 3, 'class': 'form-control form-control-sm'}),
            'category': forms.Select(attrs={'class': 'form-select form-select-sm'}),
            'file_upload': forms.FileInput(attrs={'class': 'form-control form-control-sm', 'accept': '.pdf'}),
            'logo': forms.FileInput(attrs={'class': 'form-control form-control-sm', 'accept': '.jpg,.jpeg,.png'}),
        }

class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ['name', 'email', 'message']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Your Name', 'class': 'form-control form-control-sm'}),
            'email': forms.EmailInput(attrs={'placeholder': 'your.email@example.com', 'class': 'form-control form-control-sm'}),
            'message': forms.Textarea(attrs={'placeholder': 'Your feedback', 'rows': 3, 'class': 'form-control form-control-sm'}),
        }