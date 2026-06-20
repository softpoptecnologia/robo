document.addEventListener("DOMContentLoaded", () => {
    const menuBtn = document.querySelector("[data-menu-toggle]");
    const overlay = document.querySelector(".sidebar-overlay");

    function closeNav() {
        document.body.classList.remove("nav-open");
    }

    menuBtn?.addEventListener("click", () => {
        document.body.classList.toggle("nav-open");
    });

    overlay?.addEventListener("click", closeNav);

    document.querySelectorAll(".sidebar-nav a, .bottom-nav a").forEach((link) => {
        link.addEventListener("click", () => {
            if (window.innerWidth <= 768) closeNav();
        });
    });
});
