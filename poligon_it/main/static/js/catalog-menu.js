document.addEventListener("DOMContentLoaded", function () {
    const megaMenuToggle = document.getElementById("megaMenuToggle");
    const megaMenuContent = document.querySelector(".megamenu-content");
    megaMenuContent.style.display = "none";
    megaMenuToggle.addEventListener("mouseenter", function () {
        megaMenuContent.style.display = "flex";
    });

    megaMenuContent.addEventListener("mouseleave", function () {
        megaMenuContent.style.display = "none";
    });
    document.addEventListener("click", function (event) {
        if (!megaMenuToggle.contains(event.target) && !megaMenuContent.contains(event.target)) {
            megaMenuContent.style.display = "none";
        }
    });
});
