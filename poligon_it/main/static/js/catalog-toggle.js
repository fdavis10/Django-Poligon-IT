document.addEventListener("DOMContentLoaded", function () {
    const categories = document.querySelectorAll(".category-item");
    const subcategoryGroups = document.querySelectorAll(".subcategory-group");
    
    categories.forEach(category => {
        category.addEventListener("mouseenter", function () {
            const subcategoryList = this.querySelector(".subcategory-group");
            subcategoryGroups.forEach(group => group.classList.add("hidden"));
            if (subcategoryList) {
                subcategoryList.classList.remove("hidden");
            }
        });
    });
    const subcategories = document.querySelectorAll(".subcategory-item");

    subcategories.forEach(subcategory => {
        subcategory.addEventListener("mouseenter", function () {
            const subSubcategoryList = this.querySelector(".subsubcategory-group");
            document.querySelectorAll(".subsubcategory-group").forEach(group => group.classList.add("hidden"));и
            if (subSubcategoryList) {
                subSubcategoryList.classList.remove("hidden");
            }
        });
    });
});
