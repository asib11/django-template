from django.contrib import admin
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

from projectile import env
from . import models


admin.site.unregister(Group)
admin.site.register(models.Setting)


admin.site.site_header = env.PROJECT_NAME
admin.site.site_title = env.PROJECT_NAME
admin.site.index_title = env.PROJECT_NAME



@admin.register(models.User)
class UserAdmin(BaseUserAdmin):
    fieldsets = (
        (
            None,
            {"fields": (
                    "username",
                    "password"
                )
            }
        ),
        (
            _("Personal info"),
            {
                "fields": (
                    "first_name",
                    "last_name",
                    "email",
                    "image",
                    "address1",
                    "address2",
                    "phone1",
                    "phone2",
                    "phone3",
                )
            }
        ),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "designation",
                    "status",
                    "role",
                    "user_permissions",
                ),
            },
        ),
        (
            _("Important dates"),
            {
                "fields": (
                        "last_login",
                        "date_joined",
                        "last_active_at",
                    )
                }
            ),
    )
    list_filter = (
        'status',
        'role',
    )
    list_display = (
        "username",
        "email",
        "role",
        "first_name",
        "last_name",
        "is_staff",
    )
