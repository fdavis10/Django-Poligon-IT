document.addEventListener("DOMContentLoaded", function () {
    const heroText = document.querySelector(".hero-text");
    heroText.style.opacity = "0";
    heroText.style.transform = "translateY(-20px)";

    setTimeout(() => {
        heroText.style.transition = "opacity 1s ease, transform 1s ease";
        heroText.style.opacity = "1";
        heroText.style.transform = "translateY(0)";
    }, 500);

    const featureBoxes = document.querySelectorAll(".feature-box");
    featureBoxes.forEach(box => {
        box.addEventListener("mouseover", () => {
            box.style.backgroundColor = "#f8f9fa";
        });
        box.addEventListener("mouseleave", () => {
            box.style.backgroundColor = "";
        });
    });
});
