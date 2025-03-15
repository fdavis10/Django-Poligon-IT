document.addEventListener('DOMContentLoaded', function() {

  const searchButton = document.getElementById('searchButton');
  const searchInput = document.getElementById('searchInput');


  searchButton.addEventListener('click', function() {

      searchInput.classList.toggle('show');
      

      if (searchInput.classList.contains('show') && searchInput.value.trim() !== '') {
          window.location.href = `/search/?q=${encodeURIComponent(searchInput.value)}`;
      }
  });


  searchInput.addEventListener('keypress', function(event) {
      if (event.key === 'Enter' && searchInput.value.trim() !== '') {
          event.preventDefault();  
          window.location.href = `/search/?q=${encodeURIComponent(searchInput.value)}`;
      }
  });
});

