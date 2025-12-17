from django.db import models
from common.enums import STATUS



class BaseModel(models.Model):
    status = models.SmallIntegerField(choices=STATUS.choices, default=STATUS.ACTIVE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

