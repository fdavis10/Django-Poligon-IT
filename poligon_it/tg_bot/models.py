from django.db import models

class TelegramUser(models.Model):
    chat_id = models.BigIntegerField(unique=True)
    username = models.CharField(max_length=255, blank=True, null=True)
    is_admin = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Пользователь: {self.username or self.chat_id}'
    
class ProductOrder(models.Model):
    name = models.CharField(max_length=255)
    product_name = models.CharField(max_length=1024)
    quantity = models.PositiveIntegerField()
    contact_info = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Заказ {self.id}: Пользователь --> {self.name}'

class UserQuestion(models.Model):
    chat_id = models.BigIntegerField()
    username = models.CharField(max_length=255, blank=True, null=True)
    question_text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Вопрос от {self.chat_id} --> {self.question_text[:50]}'
    
    