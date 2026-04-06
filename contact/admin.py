from django.contrib import admin
from .models import Terms, Policy, FAQ, ContactUs

@admin.register(ContactUs)
class ContactUsAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'email', 'phone_number', 'is_replied', 'created_at')
    search_fields = ('full_name', 'email', 'phone_number')
    list_filter = ('is_replied', 'created_at')
    
admin.site.register(Policy)
admin.site.register(FAQ)
admin.site.register(Terms)

