from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
import os
import logging

logger = logging.getLogger(__name__)

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

def validate_address_proof(value):
    """Validate that the uploaded file is a PDF, JPG, JPEG, or PNG."""
    ext = os.path.splitext(value.name)[1].lower()
    valid_extensions = ['.pdf', '.jpg', '.jpeg', '.png']
    if ext not in valid_extensions:
        raise ValidationError('Only PDF, JPG, JPEG, or PNG files are allowed.')

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
    host = models.CharField(max_length=100, default='smtp.gmail.com')
    port = models.PositiveIntegerField(default=587)
    use_tls = models.BooleanField(default=True)
    purpose = models.CharField(max_length=20, choices=PURPOSE_CHOICES)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.email_id} ({self.get_purpose_display()})"

    def save(self, *args, **kwargs):
        super().save(using='server', *args, **kwargs)
        try:
            super().save(using='default', *args, **kwargs)
        except Exception as e:
            logger.error(f"Failed to save to local database: {str(e)}")
            raise

class Consumer(models.Model):
    name = models.CharField(max_length=100)
    contact = models.EmailField(max_length=254)
    services = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        super().save(using='server', *args, **kwargs)
        try:
            super().save(using='default', *args, **kwargs)
        except Exception as e:
            logger.error(f"Failed to save to local database: {str(e)}")
            raise

class Business(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('suspended', 'Suspended'),
        ('rejected', 'Rejected'),
    )
    MODE_CHOICES = (
        ('online', 'Online'),
        ('offline', 'Offline'),
        ('mixed', 'Mixed'),
    )
    CATEGORY_CHOICES = (
        ('agriculture_farming', 'Agriculture & Farming'),
        ('mining_extraction', 'Mining & Extraction'),
        ('manufacturing', 'Manufacturing'),
        ('construction_infrastructure', 'Construction & Infrastructure'),
        ('retail_wholesale', 'Retail & Wholesale'),
        ('food_beverage', 'Food & Beverage Services'),
        ('hospitality_tourism', 'Hospitality & Tourism'),
        ('healthcare_wellness', 'Healthcare & Wellness'),
        ('financial_services', 'Financial Services'),
        ('education_training', 'Education & Training'),
        ('it_ites', 'Information Technology (IT & ITeS)'),
        ('media_entertainment', 'Media & Entertainment'),
        ('logistics_transportation', 'Logistics & Transportation'),
        ('professional_consulting', 'Professional & Consulting Services'),
        ('telecommunications', 'Telecommunications'),
        ('energy_utilities', 'Energy & Utilities'),
        ('real_estate', 'Real Estate & Property Services'),
        ('security_safety', 'Security & Safety Services'),
        ('creative_design', 'Creative & Design Services'),
        ('non_profit', 'Non-Profit & Social Enterprises'),
    )
    name = models.CharField(max_length=100)
    contact = models.EmailField(max_length=254)
    state = models.CharField(max_length=50, null=True, blank=True)
    district = models.CharField(max_length=50, null=True, blank=True)
    business_mode = models.CharField(max_length=20, choices=MODE_CHOICES, null=True, blank=True)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, null=True, blank=True)
    contact_number = models.CharField(max_length=15, null=True, blank=True)
    applier_designation = models.CharField(max_length=100, null=True, blank=True)
    registration_proof = models.FileField(upload_to='uploads/registration/', validators=[validate_pdf], null=True, blank=True)
    address_proof = models.FileField(upload_to='uploads/address/', validators=[validate_address_proof], null=True, blank=True)
    logo = models.ImageField(upload_to='logos/', blank=True, null=True, validators=[validate_image])
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    approved_date = models.DateTimeField(blank=True, null=True)
    suspended_date = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        super().save(using='server', *args, **kwargs)
        try:
            super().save(using='default', *args, **kwargs)
        except Exception as e:
            logger.error(f"Failed to save to local database: {str(e)}")
            raise

class Testimonial(models.Model):
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=50)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        super().save(using='server', *args, **kwargs)
        try:
            super().save(using='default', *args, **kwargs)
        except Exception as e:
            logger.error(f"Failed to save to local database: {str(e)}")
            raise

class Feedback(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(max_length=254)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        super().save(using='server', *args, **kwargs)
        try:
            super().save(using='default', *args, **kwargs)
        except Exception as e:
            logger.error(f"Failed to save to local database: {str(e)}")
            raise

class BlogImage(models.Model):
    blog = models.ForeignKey('Blog', related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='blogs/', validators=[validate_image])
    caption = models.CharField(max_length=200, blank=True, null=True)

    def __str__(self):
        return f"{self.blog.title} - Image {self.id}"

    def save(self, *args, **kwargs):
        super().save(using='server', *args, **kwargs)
        try:
            super().save(using='default', *args, **kwargs)
        except Exception as e:
            logger.error(f"Failed to save to local database: {str(e)}")
            raise

class Blog(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        super().save(using='server', *args, **kwargs)
        try:
            super().save(using='default', *args, **kwargs)
        except Exception as e:
            logger.error(f"Failed to save to local database: {str(e)}")
            raise

class SocialPlatform(models.Model):
    PLATFORM_CHOICES = (
        ('facebook', 'Facebook'),
        ('twitter', 'Twitter'),
        ('instagram', 'Instagram'),
        ('linkedin', 'LinkedIn'),
        ('youtube', 'YouTube'),
        ('pinterest', 'Pinterest'),
        ('tiktok', 'TikTok'),
    )
    name = models.CharField(max_length=50, choices=PLATFORM_CHOICES, unique=True)
    link = models.URLField(max_length=200)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.get_name_display()} - {self.link}"

    def save(self, *args, **kwargs):
        super().save(using='server', *args, **kwargs)
        try:
            super().save(using='default', *args, **kwargs)
        except Exception as e:
            logger.error(f"Failed to save to local database: {str(e)}")
            raise

class Service(models.Model):
    icon = models.CharField(max_length=50, blank=True, null=True, help_text="Enter Font Awesome icon class (e.g., 'fas fa-handshake') or leave blank if uploading an icon image.")
    icon_image = models.ImageField(upload_to='service_icons/', blank=True, null=True, validators=[validate_image], help_text="Upload a custom icon image (JPG, JPEG, PNG) if preferred.")
    name = models.CharField(max_length=100)
    description = models.TextField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        super().save(using='server', *args, **kwargs)
        try:
            super().save(using='default', *args, **kwargs)
        except Exception as e:
            logger.error(f"Failed to save to local database: {str(e)}")
            raise