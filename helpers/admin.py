from django.contrib import admin
from django.db.models.query import QuerySet


@admin.action(description="Activate selected items")
def activate_items(modeladmin, request, queryset: QuerySet):
    queryset.update(active=True)


@admin.action(description="Deactivate selected items")
def deactivate_items(modeladmin, request, queryset: QuerySet):
    queryset.update(active=False)
