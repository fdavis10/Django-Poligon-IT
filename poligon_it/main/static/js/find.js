$(document).ready(function () {
    console.log("find.js подключен!"); 

    $('#search-form-btn').on('click', function(e) {
        e.preventDefault();
        let form = $(this).closest('.search-form');
        let inputSearch = form.find('.form-control');

        if (inputSearch.hasClass('show')) {
            if (inputSearch.val().trim() === "") {
                inputSearch.removeClass('show').css('width', '0');
            } else {
                form.submit();
            }
        } else {
            inputSearch.addClass('show').css('width', '250px').focus();
        }
    });
});
