from django.utils import timezone
from django.db import models
from django.contrib.auth.models import AbstractUser

from common.models import BaseModel
from common.enums import STATUS
from .enums import USER_ROLE
import re
import uuid



class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    last_active_at = models.DateTimeField(default=timezone.now, null=True, blank=True)
    status = models.SmallIntegerField(choices=STATUS.choices, default=STATUS.ACTIVE)
    role = models.CharField(max_length=255, choices=USER_ROLE.choices, default=USER_ROLE.USER)
    image = models.ImageField(upload_to='profile', null=True, blank=True)
    address1 = models.CharField(max_length=500, null=True, blank=True)
    phone1 = models.CharField(max_length=20, null=True, blank=True)


    def update_last_active(self, update_db=True):
        self.last_active_at = timezone.now()
        if update_db:
            User.objects.filter(
                pk=self.pk
            ).update(
                last_active_at=self.last_active_at
            )

    def set_new_username(self):
        email = self.email
        name = email.split('@')[0]
        base_name = re.sub(r'\d+$', '', name)
        existing = User.objects.filter(
            username__regex=rf'^{re.escape(base_name)}\d*$'
        ).count()
        
        self.username = base_name + str(existing + 1)

class PasswordForgetOTP(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    otp = models.CharField(max_length=6)
    is_used = models.BooleanField(default=False)
    
    def is_expired(self):
        return timezone.now() > self.created_at + timezone.timedelta(minutes=5)
