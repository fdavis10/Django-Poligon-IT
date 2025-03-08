from django.contrib import admin
from django.contrib import messages
from .models import EmailCampaign
from .utils import send_bulk_email

@admin.action(description="Отправить email рассылку (по последнему шаблону)")
def send_email_to_all(modeladmin, request, queryset):
    result = send_bulk_email()
    messages.success(request, result)



class EmailCampaingAdmin(admin.ModelAdmin):
    list_display = ('subject', 'created_at')
    actions = [send_email_to_all]

admin.site.register(EmailCampaign, EmailCampaingAdmin)