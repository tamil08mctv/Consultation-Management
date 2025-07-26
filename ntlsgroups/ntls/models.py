from django.db import models
from django.core.exceptions import ValidationError

def validate_pdf(file):
    if not file.name.endswith('.pdf'):
        raise ValidationError('File must be a PDF.')

def validate_image(file):
    valid_extensions = ['.jpg', '.jpeg', '.png']
    if not any(file.name.lower().endswith(ext) for ext in valid_extensions):
        raise ValidationError('File must be JPG, JPEG, or PNG.')
    if file.size > 5 * 1024 * 1024:  # 5MB limit
        raise ValidationError('File size must be under 5MB.')

class Consumer(models.Model):
    name = models.CharField(max_length=100)
    contact = models.EmailField()
    services = models.TextField()
    budget = models.CharField(max_length=50)
    submission_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Consumer'
        verbose_name_plural = 'Consumers'

class Business(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    name = models.CharField(max_length=100)
    contact = models.EmailField()
    services = models.TextField()
    category = models.CharField(max_length=50)
    file_upload = models.FileField(upload_to='uploads/', validators=[validate_pdf])
    logo = models.ImageField(upload_to='logos/', validators=[validate_image], blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    submission_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Business'
        verbose_name_plural = 'Businesses'

class Partner(models.Model):
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=50)
    description = models.TextField()
    logo = models.ImageField(upload_to='logos/', blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Partner'
        verbose_name_plural = 'Partners'

class Testimonial(models.Model):
    name = models.CharField(max_length=100)
    message = models.TextField()
    category = models.CharField(max_length=50)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Testimonial'
        verbose_name_plural = 'Testimonials'

class Feedback(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    message = models.TextField()
    submission_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Feedback'
        verbose_name_plural = 'Feedback'