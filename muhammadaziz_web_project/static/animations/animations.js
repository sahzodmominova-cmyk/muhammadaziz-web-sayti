/* MUHAMMADAZIZ WEB SAYTI
   7 TA ANIMATSIYA
*/

document.addEventListener("DOMContentLoaded", function () {

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

            const count = Math.floor(
                (canvas.width * canvas.height) / 9000
            );

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

            requestAnimationFrame(drawStars);
        }

        resizeStars();

        window.addEventListener(
            "resize",
            resizeStars
        );

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

        playTypewriter();
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
