from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
import os
import logging
from ckeditor_uploader.fields import RichTextUploadingField

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

class Consumer(models.Model):
    name = models.CharField(max_length=100)
    contact = models.EmailField(max_length=254)
    services = models.TextField()
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
    state = models.CharField(max_length=50, null=False, blank=False)
    district = models.CharField(max_length=50, null=False, blank=False)
    business_mode = models.CharField(max_length=20, choices=MODE_CHOICES, null=False, blank=False)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, null=False, blank=False)
    contact_number = models.CharField(max_length=21, null=False, blank=False)
    applier_designation = models.CharField(max_length=100, null=False, blank=False)
    registration_proof = models.FileField(upload_to='uploads/registration/', validators=[validate_pdf], null=False, blank=False)
    address_proof = models.FileField(upload_to='uploads/address/', validators=[validate_address_proof], null=True, blank=True)
    logo = models.ImageField(upload_to='logos/', validators=[validate_image], null=False, blank=False)
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

class BlogImage(models.Model):
    blog = models.ForeignKey('Blog', related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='blogs/', validators=[validate_image])
    caption = models.CharField(max_length=200, blank=True, null=True)

    def __str__(self):
        return f"{self.blog.title} - Image {self.id}"

class Blog(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class SocialPlatform(models.Model):
    PLATFORM_CHOICES = (
        ('facebook', 'Facebook'),
        ('twitter', 'Twitter'),
        ('instagram', 'Instagram'),
        ('linkedin', 'LinkedIn'),
        ('youtube', 'YouTube'),
        ('pinterest', 'Pinterest'),
        ('tiktok', 'TikTok'),
        ('whatsapp', 'Whatsapp')
    )
    name = models.CharField(max_length=50, choices=PLATFORM_CHOICES, unique=True)
    link = models.URLField(max_length=200)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.get_name_display()} - {self.link}"

class Service(models.Model):
    icon = models.CharField(max_length=50, blank=True, null=True, help_text="Enter Font Awesome icon class (e.g., 'fas fa-handshake') or leave blank if uploading an icon image.")
    icon_image = models.ImageField(upload_to='service_icons/', blank=True, null=True, validators=[validate_image], help_text="Upload a custom icon image (JPG, JPEG, PNG) if preferred.")
    name = models.CharField(max_length=100)
    description = models.TextField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class PaymentLink(models.Model):
    link = models.URLField(max_length=200, unique=True, help_text="Enter the payment link to redirect users.")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.link

class ContactInfo(models.Model):
    phone = models.CharField(max_length=15, unique=True, help_text="Enter the contact phone number (e.g., +91-123-456-7890)")
    email = models.EmailField(max_length=254, unique=True, help_text="Enter the contact email address")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.phone} - {self.email}"

# ntls/models.py
from django.db import models
from django.conf import settings
import os

# === AT THE END OF YOUR models.py ===

class Project(models.Model):
    college_name = models.CharField("College Name", max_length=200)
    project_name = models.CharField("Project Name", max_length=200)
    instructions = models.TextField("Instructions for Students", blank=True)
    is_active = models.BooleanField("Show to Students", default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.college_name} - {self.project_name}"

    def csv_path(self):
        safe = "".join(c for c in f"{self.college_name}_{self.project_name}" if c.isalnum() or c in (" ", "_", "-"))
        return os.path.join(settings.MEDIA_ROOT, 'submissions', f"{safe}_submissions.csv")


class ProjectField(models.Model):
    TYPE_CHOICES = [
        ('text', 'Short Text'), ('textarea', 'Long Text'), ('email', 'Email'),
        ('number', 'Number'), ('date', 'Date'), ('select', 'Dropdown'),
        ('file', 'File Upload'), ('url', 'Link/URL'),
    ]

    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='fields')
    label = models.CharField("Field Label (e.g. Full Name)", max_length=200)
    field_type = models.CharField("Field Type", max_length=20, choices=TYPE_CHOICES)
    options = models.TextField("Dropdown Options (one per line)", blank=True)
    required = models.BooleanField("Required", default=False)
    unique_key = models.BooleanField(
        "Unique Key - Prevent Duplicate",
        default=False,
        help_text="Check this for Roll Number, Month, etc. Student cannot submit twice with same value"
    )
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.label


class ProjectFile(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='guidelines')
    title = models.CharField("File Title", max_length=200)
    file = models.FileField(upload_to='guidelines/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class Submission(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='submissions')
    submitted_at = models.DateTimeField(auto_now_add=True)
    data = models.JSONField(default=dict)

    def __str__(self):
        name = self.data.get('Full Name') or self.data.get('Name') or 'Unknown'
        roll = self.data.get('Roll Number') or self.data.get('Regno') or 'N/A'
        return f"{name} ({roll})"

    def get_file_links(self):
        links = []
        for key, value in self.data.items():
            if isinstance(value, str) and value.startswith('/media/'):
                links.append((key, value))
        return links

    class Meta:
        ordering = ['-submitted_at']


from django.db import models
from django.utils import timezone
from decimal import Decimal


class Event(models.Model):
    PRICE_TYPE_CHOICES = (
        ("free", "Free"),
        ("fixed", "Fixed Price"),
        ("team", "Team-based Pricing"),
    )

    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, help_text="Unique URL identifier")
    short_description = models.CharField(max_length=300)
    description = RichTextUploadingField(  # ← CHANGE THIS LINE
        help_text="Write detailed event description with formatting, images, links, etc."
    )
    registration_start = models.DateTimeField()
    registration_end = models.DateTimeField()
    price_type = models.CharField(max_length=10, choices=PRICE_TYPE_CHOICES, default="free")
    fixed_price = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    team_price_slabs = models.JSONField(
        null=True,
        blank=True,
        help_text="Example: {'2': 400, '3': 550, '4': 700} → price for team size"
    )
    max_team_size = models.PositiveIntegerField(default=1, help_text="Maximum members including leader")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def is_registration_open(self):
        now = timezone.now()
        return self.registration_start <= now <= self.registration_end

    def get_price(self, team_size=1):
        if self.price_type == "free":
            return Decimal('0')
        elif self.price_type == "fixed":
            return self.fixed_price or Decimal('0')
        elif self.price_type == "team":
            return Decimal(self.team_price_slabs.get(str(team_size), 0))
        return Decimal('0')

    def __str__(self):
        return self.title


YEAR_CHOICES = [
    ('1', '1st Year'),
    ('2', '2nd Year'),
    ('3', '3rd Year'),
    ('4', '4th Year'),
    ('other', 'Others'),
]


class EventRegistration(models.Model):
    PAYMENT_STATUS_CHOICES = (
        ("paid", "Paid"),
        ("failed", "Failed"),
    )

    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="registrations")
    name = models.CharField("Leader Full Name", max_length=150)
    email = models.EmailField()
    phone = models.CharField("Phone/WhatsApp", max_length=20)
    institution = models.CharField("College/School", max_length=255)
    year = models.CharField(max_length=10, choices=YEAR_CHOICES)
    department = models.CharField(max_length=200, blank=True)

    team_size = models.PositiveIntegerField(default=1)
    members = models.JSONField(
        null=True,
        blank=True,
        help_text="List of additional members: [{'name': ..., 'email': ..., ...}]"
    )

    amount = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    payment_status = models.CharField(max_length=10, choices=PAYMENT_STATUS_CHOICES, default="paid")
    payment_id = models.CharField(max_length=255, blank=True)  # Razorpay order ID
    razorpay_payment_id = models.CharField(max_length=255, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} – {self.event.title} ({self.get_payment_status_display()})"


class RazorpayConfig(models.Model):
    key_id = models.CharField("Razorpay Key ID", max_length=100)
    key_secret = models.CharField("Razorpay Key Secret", max_length=100)
    is_active = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Razorpay ({'Active' if self.is_active else 'Inactive'})"

    class Meta:
        verbose_name_plural = "Razorpay Configuration"

    def save(self, *args, **kwargs):
        if self.is_active:
            RazorpayConfig.objects.exclude(pk=self.pk).update(is_active=False)
        super().save(*args, **kwargs)