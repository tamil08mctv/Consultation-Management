from django import forms
from .models import Consumer, Business, Feedback

class ConsumerForm(forms.ModelForm):
    class Meta:
        model = Consumer
        fields = ['name', 'contact', 'services']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Your Name', 'class': 'form-control form-control-sm'}),
            'contact': forms.EmailInput(attrs={'placeholder': 'your.email@example.com', 'class': 'form-control form-control-sm'}),
            'services': forms.Textarea(attrs={'placeholder': 'Describe your needs', 'rows': 3, 'class': 'form-control form-control-sm'}),
        }

class BusinessForm(forms.ModelForm):
    class Meta:
        model = Business
        fields = ['name', 'contact', 'state', 'district', 'business_mode', 'category', 'contact_number', 'applier_designation', 'registration_proof', 'address_proof', 'logo']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Business Name', 'class': 'form-control form-control-sm'}),
            'contact': forms.EmailInput(attrs={'placeholder': 'business.email@example.com', 'class': 'form-control form-control-sm'}),
            'state': forms.TextInput(attrs={'placeholder': 'e.g., Tamil Nadu', 'class': 'form-control form-control-sm'}),
            'district': forms.TextInput(attrs={'placeholder': 'e.g., Chennai', 'class': 'form-control form-control-sm'}),
            'business_mode': forms.Select(attrs={'class': 'form-select form-select-sm'}),
            'category': forms.Select(attrs={'class': 'form-select form-select-sm'}),
            'contact_number': forms.TextInput(attrs={'placeholder': 'e.g., +91 9876543210', 'class': 'form-control form-control-sm'}),
            'applier_designation': forms.TextInput(attrs={'placeholder': 'e.g., CEO', 'class': 'form-control form-control-sm'}),
            'registration_proof': forms.FileInput(attrs={'class': 'form-control form-control-sm', 'accept': '.pdf'}),
            'address_proof': forms.FileInput(attrs={'class': 'form-control form-control-sm', 'accept': '.pdf,.jpg,.jpeg,.png'}),
            'logo': forms.FileInput(attrs={'class': 'form-control form-control-sm', 'accept': '.jpg,.jpeg,.png'}),
        }

    def clean_contact_number(self):
        contact_number = self.cleaned_data['contact_number']
        if contact_number and (not contact_number.startswith('+91') or len(contact_number) != 13 or not contact_number[3:].isdigit()):
            raise forms.ValidationError('Contact number must be in the format +91XXXXXXXXXX (12 digits).')
        return contact_number
    
class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ['name', 'email', 'message']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Your Name', 'class': 'form-control form-control-sm'}),
            'email': forms.EmailInput(attrs={'placeholder': 'your.email@example.com', 'class': 'form-control form-control-sm'}),
            'message': forms.Textarea(attrs={'placeholder': 'Your feedback', 'rows': 3, 'class': 'form-control form-control-sm'}),
        }