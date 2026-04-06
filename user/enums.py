from django.db import models


class USER_ROLE(models.TextChoices):
    SUPER_ADMIN = 'SUPER_ADMIN'
    ADMIN = 'ADMIN'
    USER = 'USER'


class SUBSCRIPTION_TYPE(models.TextChoices):
    BASIC = "BASIC"
    STANDARD = "STANDARD"
    PREMIUM = "PREMIUM"
    PRO = "PRO"
    ENTERPRISE = "ENTERPRISE"
