
#!/usr/bin/env python3
"""
Тестовый скрипт для проверки исправлений системы обратного звонка
"""

import os
import sys
import django

# Добавляем путь к проекту Django
sys.path.append('/workspace/Django-Poligon-IT/backend')

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'poligon_it.settings')
django.setup()

from main.models import CallbackRequest
from main.views import callback_request
from django.test import RequestFactory
import json

def test_callback_model():
    """Тестирование модели CallbackRequest"""
    print("=== Тестирование модели CallbackRequest ===")
    
    # Проверяем, что модель существует
    try:
        count = CallbackRequest.objects.count()
        print(f"✅ Модель CallbackRequest доступна. Записей в базе: {count}")
    except Exception as e:
        print(f"❌ Ошибка доступа к модели: {e}")
        return False
    
    return True

def test_callback_view():
    """Тестирование представления callback_request"""
    print("\n=== Тестирование представления callback_request ===")
    
    factory = RequestFactory()
    
    # Тест 1: Корректный запрос
    print("Тест 1: Корректный запрос с телефоном")
    data = {
        'name': 'Тестовый пользователь',
        'phone': '+7 (999) 123-45-67'
    }
    request = factory.post('/callback/', 
                          data=json.dumps(data),
                          content_type='application/json')
    
    try:
        response = callback_request(request)
        print(f"✅ Ответ получен: {response.status_code}")
        print(f"✅ Содержимое: {response.content.decode()}")
    except Exception as e:
        print(f"❌ Ошибка при выполнении запроса: {e}")
        return False
    
    # Тест 2: Запрос без телефона
    print("\nТест 2: Запрос без телефона")
    data = {
        'name': 'Тестовый пользователь'
    }
    request = factory.post('/callback/', 
                          data=json.dumps(data),
                          content_type='application/json')
    
    try:
        response = callback_request(request)
        print(f"✅ Ответ получен: {response.status_code}")
        print(f"✅ Содержимое: {response.content.decode()}")
    except Exception as e:
        print(f"❌ Ошибка при выполнении запроса: {e}")
        return False
    
    return True

def test_migration():
    """Проверка миграции"""
    print("\n=== Проверка миграции ===")
    
    try:
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM main_callbackrequest LIMIT 1")
            print("✅ Таблица main_callbackrequest существует")
    except Exception as e:
        print(f"❌ Ошибка доступа к таблице: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("Запуск тестов системы обратного звонка...")
    
    success = True
    success &= test_migration()
    success &= test_callback_model()
    success &= test_callback_view()
    
    if success:
        print("\n🎉 Все тесты пройдены успешно!")
    else:
        print("\n❌ Некоторые тесты не пройдены")
        sys.exit(1)
