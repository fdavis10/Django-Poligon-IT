document.addEventListener('DOMContentLoaded', function() {
  // Получаем элементы
  const searchButton = document.getElementById('searchButton');
  const searchInput = document.getElementById('searchInput');

  // Слушаем клик по кнопке поиска
  searchButton.addEventListener('click', function() {
      // Показываем поле поиска
      searchInput.classList.toggle('show');
      
      // Если поле уже видно и есть текст, отправляем запрос
      if (searchInput.classList.contains('show') && searchInput.value.trim() !== '') {
          window.location.href = `/search/?q=${encodeURIComponent(searchInput.value)}`;
      }
  });

  // Слушаем нажатие Enter в поле поиска
  searchInput.addEventListener('keypress', function(event) {
      if (event.key === 'Enter' && searchInput.value.trim() !== '') {
          event.preventDefault();  // Останавливаем стандартное поведение
          window.location.href = `/search/?q=${encodeURIComponent(searchInput.value)}`;
      }
  });
});
