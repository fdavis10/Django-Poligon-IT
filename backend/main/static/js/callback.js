// JavaScript для виджета обратного звонка
document.addEventListener('DOMContentLoaded', function() {
    const callbackIcon = document.getElementById('callbackIcon');
    const callbackModal = document.getElementById('callbackModal');
    const closeCallbackModal = document.getElementById('closeCallbackModal');
    const callbackForm = document.getElementById('callbackForm');
    const callbackPhone = document.getElementById('callbackPhone');

    // Получение CSRF токена
    const csrftoken = getCookie('csrftoken');

    // Маска для телефона
    if (callbackPhone) {
        callbackPhone.addEventListener('input', function(e) {
            let value = e.target.value.replace(/\D/g, '');
            let formattedValue = '';
            
            if (value.length > 0) {
                formattedValue = '+7 (';
                if (value.length > 1) {
                    formattedValue += value.substring(1, 4);
                }
                if (value.length >= 4) {
                    formattedValue += ') ' + value.substring(4, 7);
                }
                if (value.length >= 7) {
                    formattedValue += '-' + value.substring(7, 9);
                }
                if (value.length >= 9) {
                    formattedValue += '-' + value.substring(9, 11);
                }
            }
            
            e.target.value = formattedValue;
        });
    }

    // Открытие модального окна
    if (callbackIcon) {
        callbackIcon.addEventListener('click', function() {
            callbackModal.classList.add('show');
        });
    }

    // Закрытие модального окна
    if (closeCallbackModal) {
        closeCallbackModal.addEventListener('click', function() {
            callbackModal.classList.remove('show');
        });
    }

    // Закрытие при клике вне модального окна
    document.addEventListener('click', function(e) {
        if (callbackModal && callbackModal.classList.contains('show')) {
            if (!callbackModal.contains(e.target) && !callbackIcon.contains(e.target)) {
                callbackModal.classList.remove('show');
            }
        }
    });

    // Обработка отправки формы
    if (callbackForm) {
        callbackForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const formData = new FormData(callbackForm);
            const name = formData.get('name');
            const phone = formData.get('phone');
            const agreement = formData.get('agreement');
            
            // Валидация
            if (!phone || phone.replace(/\D/g, '').length < 11) {
                showMessage('Пожалуйста, введите корректный номер телефона', 'error');
                return;
            }
            
            if (!agreement) {
                showMessage('Необходимо согласие на обработку персональных данных', 'error');
                return;
            }
            
            // Отправка данных
            sendCallbackRequest(name, phone);
        });
    }

    function sendCallbackRequest(name, phone) {
        // Показываем индикатор загрузки
        const submitBtn = callbackForm.querySelector('button[type="submit"]');
        const originalText = submitBtn.textContent;
        submitBtn.textContent = 'Отправка...';
        submitBtn.disabled = true;

        // Отправка AJAX запроса на сервер
        fetch('/callback/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrftoken
            },
            body: JSON.stringify({
                name: name,
                phone: phone
            })
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            if (data.success) {
                showMessage(data.message || 'Спасибо! Мы свяжемся с вами в ближайшее время.', 'success');
                callbackForm.reset();
                callbackModal.classList.remove('show');
            } else {
                showMessage(data.error || 'Произошла ошибка. Пожалуйста, попробуйте позже.', 'error');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showMessage('Произошла ошибка. Пожалуйста, попробуйте позже.', 'error');
        })
        .finally(() => {
            // Восстанавливаем кнопку
            submitBtn.textContent = originalText;
            submitBtn.disabled = false;
        });
    }

    // Функция для показа сообщений
    function showMessage(message, type) {
        // Создаем элемент для сообщения
        const messageDiv = document.createElement('div');
        messageDiv.className = `alert alert-${type === 'success' ? 'success' : 'danger'} mt-3`;
        messageDiv.textContent = message;
        
        // Добавляем сообщение в форму
        const formBody = callbackForm.querySelector('.callback-body');
        const existingAlert = formBody.querySelector('.alert');
        if (existingAlert) {
            existingAlert.remove();
        }
        formBody.appendChild(messageDiv);
        
        // Автоматически удаляем сообщение через 5 секунд
        setTimeout(() => {
            if (messageDiv.parentNode) {
                messageDiv.remove();
            }
        }, 5000);
    }

    // Вспомогательная функция для получения CSRF токена
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
});
