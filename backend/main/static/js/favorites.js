$(document).ready(function() {
    // Обработчик для добавления товара в избранное
    $(".add-to-favorites").click(function() {
        var product_id = $(this).data('id');
        $.ajax({
            url: "{% url 'main:add_to_favorites' 0 %}".replace('0', product_id),
            method: 'POST',
            data: {
                csrfmiddlewaretoken: '{{ csrf_token }}',
            },
            success: function(response) {
                if (response.status == 'success') {
                    alert(response.message);
                }
            }
        });
    });

    // Обработчик для удаления товара из избранного
    $(".remove-favorite").click(function() {
        var product_id = $(this).data('id');
        $.ajax({
            url: "{% url 'main:remove_from_favorites' 0 %}".replace('0', product_id),
            method: 'POST',
            data: {
                csrfmiddlewaretoken: '{{ csrf_token }}',
            },
            success: function(response) {
                if (response.status == 'success') {
                    $('#product-' + product_id).remove();  // Убираем товар из списка
                }
            }
        });
    });
});