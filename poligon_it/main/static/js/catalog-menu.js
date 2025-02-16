document.addEventListener("DOMContentLoaded", function () {
    const megaMenuToggle = document.getElementById("megaMenuToggle");
    const megaMenuContent = document.querySelector(".megamenu-content");

    // Начальные стили для анимации
    megaMenuContent.style.opacity = "0";
    megaMenuContent.style.transform = "translateY(-10px)";
    megaMenuContent.style.display = "none";
    megaMenuContent.style.transition = "opacity 0.3s ease, transform 0.3s ease";

    megaMenuToggle.addEventListener("mouseenter", function () {
        megaMenuContent.style.display = "flex";
        setTimeout(() => {
            megaMenuContent.style.opacity = "1";
            megaMenuContent.style.transform = "translateY(0)";
        }, 10);
    });

    megaMenuContent.addEventListener("mouseleave", function () {
        megaMenuContent.style.opacity = "0";
        megaMenuContent.style.transform = "translateY(-10px)";
        setTimeout(() => {
            megaMenuContent.style.display = "none";
        }, 300);
    });

    document.addEventListener("click", function (event) {
        if (!megaMenuToggle.contains(event.target) && !megaMenuContent.contains(event.target)) {
            megaMenuContent.style.opacity = "0";
            megaMenuContent.style.transform = "translateY(-10px)";
            setTimeout(() => {
                megaMenuContent.style.display = "none";
            }, 300);
        }
    });
});
