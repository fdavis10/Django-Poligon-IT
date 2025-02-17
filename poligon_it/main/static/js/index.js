document.addEventListener("DOMContentLoaded", function () {
    const carousel = document.getElementById("carousel");
    const prevBtn = document.getElementById("prevBtn");
    const nextBtn = document.getElementById("nextBtn");
    
    let scrollAmount = 0;
    const scrollStep = 200;
    
    nextBtn.addEventListener("click", function () {
        carousel.scrollBy({ left: scrollStep, behavior: "smooth" });
    });

    prevBtn.addEventListener("click", function () {
        carousel.scrollBy({ left: -scrollStep, behavior: "smooth" });
    });
});

document.addEventListener("DOMContentLoaded", function () {
    console.log('slider load')
    const slider = document.querySelector(".slider");
    const slides = document.querySelectorAll(".slide");
    let index = 0;

    function nextSlide() {
        index = (index + 1) % slides.length;
        slider.style.transform = `translateX(-${index * 100}%)`;
    }

    setInterval(nextSlide, 10000);
});

document.addEventListener("DOMContentLoaded", function () {
    new Swiper(".swiper-container", {
        slidesPerView: 5, 
        spaceBetween: 0, 
        loop: true,
        navigation: {
            nextEl: ".swiper-button-next",
            prevEl: ".swiper-button-prev",
        },
        pagination: {
            el: ".swiper-pagination",
            clickable: true,
        },
        breakpoints: {
            320: { slidesPerView: 1 },
            768: { slidesPerView: 2 },
            1024: { slidesPerView: 3 },
            1320: { slidesPerView: 4 },
        }
    });
});