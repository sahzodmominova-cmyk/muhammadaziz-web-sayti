(() => {
  "use strict";
  document.documentElement.classList.add("futuristic-ready");
  const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  // Create visible, lightweight floating stars inside the hero banner.
  const hero = document.querySelector(".hero");
  if (hero && !reduceMotion && !hero.querySelector(".neo-particle")) {
    const colors = ["#43cfff", "#a78bfa", "#ffffff", "#258bff"];
    for (let i = 0; i < 38; i++) {
      const particle = document.createElement("i");
      particle.className = "neo-particle";
      particle.setAttribute("aria-hidden", "true");
      particle.style.setProperty("--particle-left", `${Math.random() * 98}%`);
      particle.style.setProperty("--particle-top", `${Math.random() * 94}%`);
      particle.style.setProperty("--particle-size", `${2 + Math.random() * 3}px`);
      particle.style.setProperty("--particle-duration", `${4 + Math.random() * 7}s`);
      particle.style.setProperty("--particle-delay", `${-Math.random() * 8}s`);
      particle.style.setProperty("--particle-dx", `${-24 + Math.random() * 48}px`);
      particle.style.setProperty("--particle-dy", `${-36 + Math.random() * 28}px`);
      particle.style.setProperty("--particle-color", colors[i % colors.length]);
      hero.appendChild(particle);
    }
  }

  // Reveal cards as they enter the viewport.
  if (!reduceMotion && "IntersectionObserver" in window) {
    const targets = document.querySelectorAll(".course, .lesson-item, #courseTestButtons > *, #ratingList > *");
    targets.forEach((el, i) => {
      el.classList.add("neo-reveal");
      el.style.setProperty("--reveal-delay", `${Math.min(i % 8, 7) * 55}ms`);
    });
    const observer = new IntersectionObserver(entries => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add("neo-visible");
          observer.unobserve(entry.target);
        }
      });
    }, { threshold: 0.08 });
    targets.forEach(el => observer.observe(el));
  }

  document.querySelectorAll('nav a[href^="#"]').forEach(link => {
    link.addEventListener("click", () => {
      document.querySelectorAll("nav a").forEach(a => a.classList.remove("nav-current"));
      link.classList.add("nav-current");
    });
  });

  // Mouse-follow glow coordinates on course cards.
  document.querySelectorAll(".course").forEach(card => {
    card.addEventListener("pointermove", e => {
      const r = card.getBoundingClientRect();
      card.style.setProperty("--pointer-x", `${e.clientX - r.left}px`);
      card.style.setProperty("--pointer-y", `${e.clientY - r.top}px`);
    });
  });
})();
