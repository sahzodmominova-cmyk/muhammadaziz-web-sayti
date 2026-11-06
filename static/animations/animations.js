/* MUHAMMADAZIZ WEB SAYTI
   7 TA ANIMATSIYA
*/

document.addEventListener("DOMContentLoaded", function () {

    /* ==================================================
       0. ♿ ANIMATSIYANI KAMAYTIRISH
       Tizim sozlamasi (prefers-reduced-motion) yoki foydalanuvchi tugmasi bo'yicha animatsiyalar o'chadi
       ================================================== */
    const reducedMotion = !!(window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches);
    function animOff() {
        let off = false;
        try { off = localStorage.getItem("anim_off") === "1"; } catch (e) {}
        return reducedMotion || off;
    }
    document.body.classList.toggle("no-anim", animOff());
    const animBtn = document.createElement("button");
    animBtn.id = "animToggle";
    animBtn.type = "button";
    function animLabel() {
        animBtn.textContent = animOff() ? "▶ Animatsiyani yoqish" : "⏸ Animatsiyani o‘chirish";
        animBtn.setAttribute("aria-pressed", String(animOff()));
    }
    animBtn.addEventListener("click", function () {
        try { localStorage.setItem("anim_off", animOff() ? "0" : "1"); } catch (e) {}
        document.body.classList.toggle("no-anim", animOff());
        animLabel();
        if (!animOff() && window.__restartStars) window.__restartStars();
    });
    if (reducedMotion) animBtn.style.display = "none";
    animLabel();
    document.body.appendChild(animBtn);

    /* ==================================================
       1. ⭐ YULDUZLI FON
       ================================================== */

    const canvas = document.getElementById("stars-canvas");

    if (canvas) {

        const ctx = canvas.getContext("2d");

        let stars = [];

        function resizeStars() {

            canvas.width = canvas.offsetWidth;
            canvas.height = canvas.offsetHeight;

            stars = [];

            const count = Math.min(140, Math.floor((canvas.width * canvas.height) / (canvas.width < 700 ? 16000 : 9000)));

            for (let i = 0; i < count; i++) {

                stars.push({
                    x: Math.random() * canvas.width,

                    y: Math.random() * canvas.height,

                    r: Math.random() * 1.5 + 0.3,

                    speed:
                        Math.random() * 0.35 + 0.05,

                    alpha:
                        Math.random() * 0.7 + 0.3
                });
            }
        }

        function drawStars() {

            ctx.clearRect(
                0,
                0,
                canvas.width,
                canvas.height
            );

            stars.forEach(function (star) {

                star.y -= star.speed;

                if (star.y < 0) {
                    star.y = canvas.height;
                    star.x =
                        Math.random() * canvas.width;
                }

                ctx.beginPath();

                ctx.arc(
                    star.x,
                    star.y,
                    star.r,
                    0,
                    Math.PI * 2
                );

                ctx.fillStyle =
                    "rgba(255,255,255," +
                    star.alpha +
                    ")";

                ctx.fill();
            });

            if (!animOff()) requestAnimationFrame(drawStars);   // animatsiya o'chiq bo'lsa, sikl to'xtaydi
        }

        resizeStars();

        window.addEventListener(
            "resize",
            resizeStars
        );

        window.__restartStars = drawStars;

        drawStars();
    }


    /* ==================================================
       2. 🌈 SUZUVCHI GRADIENT DOG'LAR
       CSS orqali ishlaydi
       ================================================== */


    /* ==================================================
       3. ✨ SHIMMER
       CSS orqali ishlaydi
       ================================================== */


    /* ==================================================
       4. ⌨️ TYPEWRITER
       ================================================== */

    const typewriter =
        document.getElementById("twText");

    if (typewriter) {

        const texts = [
            "Kompyuter savodxonligini o‘rganing",
            "Python dasturlashni o‘rganing",
            "Sun’iy intellekt bilan ishlang",
            "IT bilimlaringizni rivojlantiring",
            "Kelajagingizni bugundan boshlang"
        ];

        let textIndex = 0;
        let charIndex = 0;
        let deleting = false;

        function playTypewriter() {

            const current =
                texts[textIndex];

            if (!deleting) {

                typewriter.textContent =
                    current.substring(
                        0,
                        charIndex + 1
                    );

                charIndex++;

                if (
                    charIndex >=
                    current.length
                ) {

                    deleting = true;

                    setTimeout(
                        playTypewriter,
                        1500
                    );

                    return;
                }

            } else {

                typewriter.textContent =
                    current.substring(
                        0,
                        charIndex - 1
                    );

                charIndex--;

                if (charIndex <= 0) {

                    deleting = false;

                    textIndex =
                        (textIndex + 1) %
                        texts.length;
                }
            }

            setTimeout(
                playTypewriter,
                deleting ? 45 : 75
            );
        }

        if (animOff()) { typewriter.textContent = texts[0]; } else { playTypewriter(); }
    }


    /* ==================================================
       5. 🔆 PORLOVCHI TUGMA
       CSS orqali ishlaydi
       ================================================== */

    document
        .querySelectorAll(".glow-btn")
        .forEach(function (button) {

            button.addEventListener(
                "mouseenter",
                function () {

                    button.style.transform =
                        "translateY(-2px) scale(1.03)";
                }
            );

            button.addEventListener(
                "mouseleave",
                function () {

                    button.style.transform =
                        "";
                }
            );
        });


    /* ==================================================
       6. 🧩 KETMA-KET PAYDO BO'LISH
       ================================================== */

    const chips =
        document.querySelectorAll(
            ".stagger-row .chip"
        );

    chips.forEach(function (chip, index) {

        chip.style.animationDelay =
            (index * 0.1) + "s";
    });


    /* ==================================================
       7. 📊 PROGRESS
       CSS orqali ishlaydi
       ================================================== */


    /* ==================================================
       QO'SHIMCHA:
       animatsiyalarni qayta ishga tushirish
       ================================================== */

    window.playChips = function () {

        const items =
            document.querySelectorAll(
                ".stagger-row .chip"
            );

        items.forEach(function (item) {

            item.style.animation = "none";

            void item.offsetWidth;

            item.style.animation =
                "riseIn 0.5s ease forwards";
        });
    };

});
