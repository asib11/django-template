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

    def save(self, *args, **kwargs):
        if self.is_superuser:
            self.is_staff = True
            self.role = USER_ROLE.SUPER_ADMIN
        elif self.is_staff:
            self.role = USER_ROLE.ADMIN
        else:
            self.role = USER_ROLE.USER

        super().save(*args, **kwargs)


    def update_last_active(self, update_db=True):
        self.last_active_at = timezone.now()
        if update_db:
            User.objects.filter(
                pk=self.pk
            ).update(
                last_active_at=self.last_active_at
            )

    def set_new_username(self):
        email = self.email or ''
        name = email.split('@')[0] if '@' in email else email
        base_name = re.sub(r'\d+$', '', name) or 'user'

        existing_usernames = list(
            User.objects.filter(
                username__regex=rf'^{re.escape(base_name)}\d*$'
            ).values_list('username', flat=True)
        )

        if base_name not in existing_usernames:
            self.username = base_name
            return

        suffix_pattern = re.compile(rf'^{re.escape(base_name)}(\d+)$')
        max_suffix = 0
        for username in existing_usernames:
            match = suffix_pattern.match(username)
            if match:
                max_suffix = max(max_suffix, int(match.group(1)))

        self.username = f'{base_name}{max_suffix + 1}'

class PasswordForgetOTP(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    otp = models.CharField(max_length=6)
    is_used = models.BooleanField(default=False)
    
    def is_expired(self):
        return timezone.now() > self.created_at + timezone.timedelta(minutes=5)
