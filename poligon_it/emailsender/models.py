from django.db import models

class EmailCampaign(models.Model):
    subject = models.CharField("Тема письма", max_length=255)
    message = models.TextField("Текст письма")
    created_at = models.DateTimeField("Дата создания",auto_now_add=True)

    def __str__(self):
        return f'Рассылка письма от {self.created_at.strftime("%Y-%m-%d %H:%M")}'
