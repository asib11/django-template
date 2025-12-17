from django.utils import timezone
from django.db import models
from django.contrib.auth.models import AbstractUser

from common.models import BaseModel
from common.enums import STATUS
from .enums import USER_ROLE



class User(AbstractUser):
    last_active_at = models.DateTimeField(default=timezone.now, null=True, blank=True)
    status = models.SmallIntegerField(choices=STATUS.choices, default=STATUS.ACTIVE)
    role = models.CharField(max_length=255, choices=USER_ROLE.choices, default=USER_ROLE.SCHOOL_ADMIN)
    image = models.ImageField(upload_to='profile', null=True, blank=True)
    designation = models.CharField(max_length=255, null=True, blank=True)
    address1 = models.CharField(max_length=500, null=True, blank=True)
    address2 = models.CharField(max_length=500, null=True, blank=True)
    phone1 = models.CharField(max_length=20, null=True, blank=True)
    phone2 = models.CharField(max_length=20, null=True, blank=True)
    phone3 = models.CharField(max_length=20, null=True, blank=True)

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
        user_count = User.objects.filter(
            username__startswith=name
        ).count()
        self.username = name + str(user_count + 1)

    @classmethod
    def get_bot(cls):
        return cls.objects.filter(
            role=USER_ROLE.BOT
        ).first()

class PasswordForgetOTP(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    otp = models.CharField(max_length=5)
    is_used = models.BooleanField(default=False)
    
    def is_expired(self):
        return timezone.now() > self.created_at + timezone.timedelta(minutes=1)