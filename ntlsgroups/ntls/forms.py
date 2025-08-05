from django import forms
from django.core.exceptions import ValidationError
import re
from .models import Consumer, Business, Feedback
import os

class ConsumerForm(forms.ModelForm):
    class Meta:
        model = Consumer
        fields = ['name', 'contact', 'services']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add Bootstrap classes and placeholders
        self.fields['name'].widget.attrs.update({'class': 'form-control', 'placeholder': 'e.g., John Doe'})
        self.fields['contact'].widget.attrs.update({'class': 'form-control', 'placeholder': 'e.g., john@example.com'})
        self.fields['services'].widget.attrs.update({'class': 'form-control', 'placeholder': 'e.g., Web Development, Consulting', 'rows': 3})

    def clean_contact(self):
        contact = self.cleaned_data['contact']
        email_pattern = r'^[^\s@]+@[^\s@]+\.[^\s@]+$'
        if not re.match(email_pattern, contact):
            raise ValidationError('Please enter a valid email address.')
        return contact

class BusinessForm(forms.ModelForm):
    class Meta:
        model = Business
        fields = ['name', 'contact', 'state', 'district', 'business_mode', 'category', 'contact_number', 'applier_designation', 'registration_proof', 'address_proof', 'logo']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add Bootstrap classes and placeholders
        self.fields['name'].widget.attrs.update({'class': 'form-control', 'placeholder': 'e.g., NTLS Solutions'})
        self.fields['contact'].widget.attrs.update({'class': 'form-control', 'placeholder': 'e.g., info@ntls.com'})
        self.fields['state'].widget.attrs.update({'class': 'form-control', 'placeholder': 'e.g., Tamilnadu'})
        self.fields['district'].widget.attrs.update({'class': 'form-control', 'placeholder': 'e.g., Namakkal'})
        self.fields['business_mode'].widget.attrs.update({'class': 'form-select'})
        self.fields['category'].widget.attrs.update({'class': 'form-select'})
        self.fields['contact_number'].widget.attrs.update({'class': 'form-control', 'placeholder': 'e.g., +919629828969'})
        self.fields['applier_designation'].widget.attrs.update({'class': 'form-control', 'placeholder': 'e.g., CEO'})
        self.fields['registration_proof'].widget.attrs.update({'class': 'form-control'})
        self.fields['address_proof'].widget.attrs.update({'class': 'form-control'})
        self.fields['logo'].widget.attrs.update({'class': 'form-control'})

    def clean_contact(self):
        contact = self.cleaned_data['contact']
        email_pattern = r'^[^\s@]+@[^\s@]+\.[^\s@]+$'
        if not re.match(email_pattern, contact):
            raise ValidationError('Please enter a valid email address.')
        return contact

    def clean_contact_number(self):
        contact_number = self.cleaned_data['contact_number']
        if contact_number:
            normalized_value = contact_number.replace(' ', '').replace('-', '')
            if not re.match(r'^\+\d{1,3}\d{6,12}$', normalized_value) or len(normalized_value) < 10 or len(normalized_value) > 15:
                raise ValidationError('Contact number must be in a valid international format (e.g., +911234567890, +1-123-456-7890, or +442071234567).')
        return contact_number

    def clean_registration_proof(self):
        registration_proof = self.cleaned_data['registration_proof']
        if registration_proof:
            ext = os.path.splitext(registration_proof.name)[1].lower()
            if ext != '.pdf':
                raise ValidationError('Only PDF files are allowed for registration proof.')
        return registration_proof

    def clean_address_proof(self):
        address_proof = self.cleaned_data['address_proof']
        if address_proof:
            ext = os.path.splitext(address_proof.name)[1].lower()
            valid_extensions = ['.pdf', '.jpg', '.jpeg', '.png']
            if ext not in valid_extensions:
                raise ValidationError('Only PDF, JPG, JPEG, or PNG files are allowed for address proof.')
        return address_proof

    def clean_logo(self):
        logo = self.cleaned_data['logo']
        if logo:
            ext = os.path.splitext(logo.name)[1].lower()
            valid_extensions = ['.jpg', '.jpeg', '.png']
            if ext not in valid_extensions:
                raise ValidationError('Only JPG, JPEG, or PNG files are allowed for logo.')
            if logo.size > 5 * 1024 * 1024:  # 5MB limit
                raise ValidationError('Logo file size must be under 5MB.')
        return logo

class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ['name', 'email', 'message']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].widget.attrs.update({'class': 'form-control', 'placeholder': 'e.g., Jane Smith'})
        self.fields['email'].widget.attrs.update({'class': 'form-control', 'placeholder': 'e.g., jane@example.com'})
        self.fields['message'].widget.attrs.update({'class': 'form-control', 'placeholder': 'e.g., Your feedback here', 'rows': 4})

    def clean_email(self):
        email = self.cleaned_data['email']
        email_pattern = r'^[^\s@]+@[^\s@]+\.[^\s@]+$'
        if not re.match(email_pattern, email):
            raise ValidationError('Please enter a valid email address.')
        return email