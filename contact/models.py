from django.db import models
from common.models import BaseModel
# Create your models here.

class Terms(BaseModel):
    title = models.CharField(max_length=255, blank=True, null=True, default="Terms and Conditions")
    content = models.TextField(default="")

    class Meta:
        verbose_name = 'Terms'
        verbose_name_plural = 'Terms'

    def __str__(self):
        return self.title


class Policy(BaseModel):
    title = models.CharField(max_length=255, blank=True, null=True, default="Privacy Policy")
    content = models.TextField(default="")

    class Meta:
        verbose_name = 'Policy'
        verbose_name_plural = 'Policies'

    def __str__(self):
        return self.title


class FAQ(BaseModel):
    question = models.CharField(max_length=500)
    answer = models.TextField()
    order = models.IntegerField(default=0, help_text="Display order (lower numbers appear first)")

    class Meta:
        verbose_name = 'FAQ'
        verbose_name_plural = 'FAQs'
        ordering = ['order', '-created_at']

    def __str__(self):
        return self.question
    
class ContactUs(BaseModel):
    full_name = models.CharField(max_length=255)
    email = models.EmailField()
    phone_number = models.CharField(max_length=20)
    message = models.TextField()
    is_replied = models.BooleanField(default=False)

    def __str__(self):
        return f'Message from {self.full_name}'