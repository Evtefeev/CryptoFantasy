function lazyLoadImgs() {
    const bgElements = document.querySelectorAll(".lazy-bg");

    const observer = new IntersectionObserver(entries => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const el = entry.target;
                const img = new Image();
                img.src = el.dataset.bg;
                img.onload = () => {
                    el.style.backgroundImage = `url('${el.dataset.bg}')`;
                    el.classList.add("loaded");
                };
                observer.unobserve(el);
            }
        });
    });

    bgElements.forEach(el => observer.observe(el));
}



document.addEventListener("DOMContentLoaded", lazyLoadImgs);
