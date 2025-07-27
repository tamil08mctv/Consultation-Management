from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
import os

def validate_pdf(value):
    """Validate that the uploaded file is a PDF."""
    ext = os.path.splitext(value.name)[1].lower()
    if ext != '.pdf':
        raise ValidationError('Only PDF files are allowed.')

def validate_image(value):
    """Validate that the uploaded file is an image (jpg, jpeg, png)."""
    ext = os.path.splitext(value.name)[1].lower()
    valid_extensions = ['.jpg', '.jpeg', '.png']
    if ext not in valid_extensions:
        raise ValidationError('Only JPG, JPEG, or PNG files are allowed.')

class EmailConfig(models.Model):
    PURPOSE_CHOICES = (
        ('form_submission', 'Form Submission'),
        ('status_update', 'Status Update'),
        ('general', 'General'),
        ('notifications', 'Notifications'),
    )
    BACKEND_CHOICES = (
        ('django.core.mail.backends.smtp.EmailBackend', 'SMTP'),
        ('django.core.mail.backends.console.EmailBackend', 'Console'),
    )
    email_id = models.EmailField(max_length=254, unique=True)
    password = models.CharField(max_length=100, blank=True)
    host = models.CharField(max_length=100, default='smtp.zoho.com')
    port = models.PositiveIntegerField(default=587)
    use_tls = models.BooleanField(default=True)
    purpose = models.CharField(max_length=20, choices=PURPOSE_CHOICES)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.email_id} ({self.get_purpose_display()})"

class Consumer(models.Model):
    name = models.CharField(max_length=100)
    contact = models.EmailField(max_length=254)
    services = models.TextField()
    budget = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Business(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('suspended', 'Suspended'),
        ('rejected', 'Rejected'),
    )
    name = models.CharField(max_length=100)
    contact = models.EmailField(max_length=254)
    description = models.TextField()
    category = models.CharField(max_length=50)
    file_upload = models.FileField(upload_to='uploads/', validators=[validate_pdf])
    logo = models.ImageField(upload_to='logos/', blank=True, null=True, validators=[validate_image])
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    approved_date = models.DateTimeField(blank=True, null=True)
    suspended_date = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Testimonial(models.Model):
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=50)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Feedback(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(max_length=254)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name