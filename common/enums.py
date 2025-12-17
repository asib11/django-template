from django.db import models


class STATUS(models.IntegerChoices):
    DRAFT = 0
    ACTIVE = 1
    INACTIVE = 2
    DELETED = 3
