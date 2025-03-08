from django.core.mail import send_mail
from orders.models import Order
from .models import EmailCampaign

def send_bulk_email():
    last_campaign = EmailCampaign.objects.last()
    if not last_campaign:
        return 'Нет созданных шаблонов для рассылки. Добавьте новую в администраторской панели Django!'
    
    recipients = Order.objects.exclude(email="").values_list('email', flat=True)
    if not recipients:
        return 'Нет клиентов с EMAIL в базе данных'
    
    send_mail(
        subject=last_campaign.subject,
        message=last_campaign.message,
        from_email='test@example.com',
        recipient_list=recipients,
        fail_silently=False,
    )

    return f'Рассылка "{last_campaign.subject}" отправлена {len(recipients)} пользователям'

def send_mass_mail(subject, body):
    recipients = Order.objects.exclude(email="").values_list('email', flat=True)
    send_mail(
        subject=subject,
        message=body,
        from_email='test@example.com',
        recipient_list=list(recipients),
        fail_silently=False,
    )