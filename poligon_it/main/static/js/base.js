document.addEventListener('DOMContentLoaded', function() {
    // Получаем элементы
    const searchButton = document.getElementById('searchButton');
    const searchInput = document.getElementById('searchInput');
  
    // Слушаем клик по кнопке поиска
    searchButton.addEventListener('click', function() {
      // Переключаем класс show для поля ввода
      searchInput.classList.toggle('show');
    });
  });
  