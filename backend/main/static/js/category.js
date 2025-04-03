document.addEventListener("DOMContentLoaded", function () {
    const filterForm = document.getElementById("filter-form");
    const productList = document.querySelector(".cards_wrapper");

    filterForm.addEventListener("submit", function (event) {
        event.preventDefault(); 

        let formData = new FormData(filterForm);
        let params = new URLSearchParams(formData).toString(); 

        fetch(window.location.pathname + "?" + params, {
            method: "GET",
            headers: {
                "X-Requested-With": "XMLHttpRequest"
            }
        })
        .then(response => response.text())
        .then(data => {
            let tempDiv = document.createElement("div");
            tempDiv.innerHTML = data;

            let newProducts = tempDiv.querySelector(".cards_wrapper");
            if (newProducts) {
                productList.innerHTML = newProducts.innerHTML;
            }
        })
        .catch(error => console.error("Ошибка загрузки товаров:", error));
    });
});
