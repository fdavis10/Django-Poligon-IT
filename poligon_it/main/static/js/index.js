document.addEventListener("DOMContentLoaded", () => {
    const container = document.querySelector(".categories-wrapper");
    const categories = document.querySelectorAll(".category-box");
    const prevBtn = document.querySelector(".prev-btn");
    const nextBtn = document.querySelector(".next-btn");

    if (!container || !categories.length || !prevBtn || !nextBtn) return;

    const scrollStep = container.clientWidth / 2; 

    function scrollLeft() {
        container.scrollBy({ left: -scrollStep, behavior: "smooth" });
    }

    function scrollRight() {
        container.scrollBy({ left: scrollStep, behavior: "smooth" });
    }

    prevBtn.addEventListener("click", scrollLeft);
    nextBtn.addEventListener("click", scrollRight);

    function updateCategoryLayout() {
        let columns = 2;

        if (window.innerWidth >= 1024) {
            columns = 4;
        } else if (window.innerWidth >= 768) {
            columns = 3;
        }

        categories.forEach(category => {
            category.style.flex = `0 0 calc(${100 / columns}% - 20px)`;
        });

        if (window.innerWidth < 1024) {
            prevBtn.style.display = "none";
            nextBtn.style.display = "none";
        } else {
            prevBtn.style.display = "block";
            nextBtn.style.display = "block";
        }
    }

    updateCategoryLayout();
    window.addEventListener("resize", updateCategoryLayout);
});
